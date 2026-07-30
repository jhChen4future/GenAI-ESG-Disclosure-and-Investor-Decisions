from otree.api import *
import json
import os
import traceback
import importlib
import socket
import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib import error as urllib_error
from urllib import request as urllib_request

doc = """
Investor Task:
1. 校准 (Calibration): 学习 Wind ESG 评分标准 (30/60/90)。
2. 阅读 (Reading): 阅读 Manager 生成的报告 (PDF)。
3. 决策 (Decision): 给出评分(0-100)和投资意愿。
4. 测试 (Quiz): 客观理解测试。
5. 结算 (Results): 计算双方收益。
"""


API_KEY = os.environ.get('API_KEY')
API_ENDPOINT = os.environ.get('API_ENDPOINT')
API_MODEL = os.environ.get('API_MODEL')
MAX_CHAT_TURNS = 10
API_TIMEOUT_SECONDS = 60
API_MAX_RETRIES = 3
API_RETRY_BACKOFF_SECONDS = 1.5
MAX_REPORT_TEXT_CHARS = 3500
MAX_CALIBRATION_TEXT_CHARS = 1200
CHAT_POLL_INTERVAL_SECONDS = 1.2

CHAT_EXECUTOR = ThreadPoolExecutor(max_workers=6)
PENDING_CHAT_JOBS = {}
PENDING_CHAT_LOCK = threading.Lock()

CALIBRATION_PDF_CONFIG = [
    {
        'score': 30,
        'filename': 'calib_30.pdf',
        'fallback': '30分样本：传统CSR活动为主，缺乏量化环境目标与前瞻性气候风险分析。',
    },
    {
        'score': 60,
        'filename': 'calib_60.pdf',
        'fallback': '60分样本：运营合规与风险控制较强，披露数据较细，但战略前瞻性不足。',
    },
    {
        'score': 90,
        'filename': 'calib_90.pdf',
        'fallback': '90分样本：ESG已融入核心战略，具备董事会治理、国际标准与供应链赋能。',
    },
]


def _load_chat_history(player):
    if not player.chat_history:
        return []
    try:
        history = json.loads(player.chat_history)
        if isinstance(history, list):
            return history
    except Exception:
        print(f"[InvestorReading][WARN] chat_history parse failed for {player.participant.code}")
        print(traceback.format_exc())
    return []


def _save_chat_history(player, history):
    player.chat_history = json.dumps(history, ensure_ascii=False)


def _extract_pdf_text(pdf_path, max_chars=MAX_CALIBRATION_TEXT_CHARS):
    if not os.path.exists(pdf_path):
        print(f"[InvestorReading][CALIB] PDF not found: {pdf_path}")
        return None

    try:
        PdfReader = None
        try:
            pypdf_module = importlib.import_module('pypdf')
            PdfReader = getattr(pypdf_module, 'PdfReader', None)
        except Exception:
            PdfReader = None

        if PdfReader is None:
            try:
                pypdf2_module = importlib.import_module('PyPDF2')
                PdfReader = getattr(pypdf2_module, 'PdfReader', None)
            except Exception:
                PdfReader = None

        if PdfReader is None:
            print('[InvestorReading][CALIB] pypdf/PyPDF2 not installed, use fallback summary.')
            return None

        reader = PdfReader(pdf_path)
        chunks = []
        for page in reader.pages:
            page_text = page.extract_text() or ''
            if page_text.strip():
                chunks.append(page_text.strip())

        text = '\n'.join(chunks).strip()
        if not text:
            print(f"[InvestorReading][CALIB] Empty extracted text: {pdf_path}")
            return None
        return text[:max_chars]
    except Exception:
        print(f"[InvestorReading][CALIB ERROR] Failed to parse PDF: {pdf_path}")
        print(traceback.format_exc())
        return None


def _build_calibration_context(player):
    cached = player.participant.vars.get('calibration_context_y2')
    if cached:
        return cached

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, '_static', 'investor_y2')

    sections = []
    for item in CALIBRATION_PDF_CONFIG:
        score = item['score']
        filename = item['filename']
        fallback = item['fallback']

        abs_path = os.path.join(static_dir, filename)
        url_path = f"/static/investor_y2/{filename}"

        pdf_text = _extract_pdf_text(abs_path)
        final_text = pdf_text if pdf_text else fallback

        sections.append(
            f"[Score={score}] file={filename} url={url_path}\n{final_text}"
        )

    context = "\n\n".join(sections)
    player.participant.vars['calibration_context_y2'] = context
    return context


def _ensure_system_message(player, history):
    if history and history[0].get('role') == 'system':
        return history

    report_text = (player.seen_report_text or '').strip()
    if not report_text:
        report_text = '暂无报告正文。'
    report_text = report_text[:MAX_REPORT_TEXT_CHARS]

    calibration_context = _build_calibration_context(player)

    system_prompt = (
        "你是 FinGPT Analyst Assistant。"
        "你正在协助用户完成一项基于企业ESG报告的评分实验。"
        "请理解当前对话与实验任务相关，并结合报告内容回答。"
        "可参考三个评分锚点：30分、60分、90分。\n\n"
        f"【评分校准样本（来自 calib_30/60/90.pdf）】\n{calibration_context}\n\n"
        f"【报告正文】\n{report_text}"
    )

    return [{'role': 'system', 'content': system_prompt}] + history


def _trim_history(history):
    if not history:
        return history
    system_msg = history[0] if history[0].get('role') == 'system' else None
    rest = history[1:] if system_msg else history
    max_items = MAX_CHAT_TURNS * 2
    if len(rest) > max_items:
        rest = rest[-max_items:]
    return ([system_msg] + rest) if system_msg else rest


def _call_openai_compatible(messages):
    required = {
        'API_KEY': API_KEY,
        'API_ENDPOINT': API_ENDPOINT,
        'API_MODEL': API_MODEL,
    }
    if any(not value for value in required.values()):
        raise RuntimeError('API_KEY, API_ENDPOINT, and API_MODEL must be set')

    url = API_ENDPOINT
    payload = {
        'model': API_MODEL,
        'messages': messages,
        'temperature': 0.4,
    }
    encoded_payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')

    for attempt in range(1, API_MAX_RETRIES + 1):
        req = urllib_request.Request(
            url=url,
            data=encoded_payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}',
            },
            method='POST',
        )

        try:
            with urllib_request.urlopen(req, timeout=API_TIMEOUT_SECONDS) as resp:
                raw = resp.read().decode('utf-8')
                data = json.loads(raw)

                choices = data.get('choices') or []
                if not choices:
                    print(f"[InvestorReading][API InvalidResponse] no choices, raw={raw[:500]}")
                    raise ValueError('API response missing choices')

                content = (choices[0].get('message') or {}).get('content', '')
                if isinstance(content, list):
                    content = '\n'.join([part.get('text', '') for part in content if isinstance(part, dict)])
                return str(content).strip()

        except urllib_error.HTTPError as exc:
            error_body = exc.read().decode('utf-8', errors='ignore') if hasattr(exc, 'read') else ''
            print(f"[InvestorReading][API HTTPError] attempt={attempt}/{API_MAX_RETRIES} status={exc.code} reason={exc.reason}")
            print(f"[InvestorReading][API HTTPError body] {error_body}")
            raise

        except (TimeoutError, socket.timeout) as exc:
            print(
                f"[InvestorReading][API Timeout] attempt={attempt}/{API_MAX_RETRIES} "
                f"timeout={API_TIMEOUT_SECONDS}s payload_bytes={len(encoded_payload)} error={exc}"
            )
            if attempt < API_MAX_RETRIES:
                time.sleep(API_RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise TimeoutError(f"API timed out after {API_MAX_RETRIES} attempts") from exc

        except urllib_error.URLError as exc:
            print(f"[InvestorReading][API URLError] attempt={attempt}/{API_MAX_RETRIES} reason={exc.reason}")
            reason = getattr(exc, 'reason', None)
            if isinstance(reason, (TimeoutError, socket.timeout)) and attempt < API_MAX_RETRIES:
                time.sleep(API_RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise

        except Exception:
            print(f"[InvestorReading][API UnknownError] attempt={attempt}/{API_MAX_RETRIES}")
            print(traceback.format_exc())
            raise

    raise RuntimeError('Unexpected API retry flow termination')


def _extract_gpt_total_score(reply_text):
    if not reply_text:
        return None

    text = str(reply_text)
    patterns = [
        r'(?:总评分|综合评分|最终评分|总体评分|总分|overall\s*score|total\s*score)\s*[:：]?\s*(\d{1,3}(?:\.\d+)?)',
        r'(\d{1,3}(?:\.\d+)?)\s*/\s*100',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 0 <= val <= 100:
                    return round(val, 2)
            except Exception:
                continue

    return None


class C(BaseConstants):
    NAME_IN_URL = 'investor_y2'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    # === 实验核心参数 ===
    TRUE_COMPANY_VALUE = 50
    MAX_ACCURACY_PAYOFF = cu(55)
    PENALTY_PER_POINT = cu(1)
    QUIZ_BONUS = cu(6)

    # 管理者收益参数
    MANAGER_BASE_PAY = cu(10)
    MANAGER_RETURN_RATE = 0.5  # 评分系数: 收益 = 10 + 0.5 * 评分

    # === 校准范例 (Calibration Anchors) ===
    EXAMPLE_LOW = {
        "score": 30,
        "label": "30分 - 起步阶段 (CSR侧重)",
        "file_path": "investor_y2/calib_30.pdf",
        "desc_short": "传统CSR活动，缺乏量化目标",
        "desc_full": "ESG管理处于起步阶段，侧重于传统的CSR（企业社会责任）活动，如捐赠、扶贫和基础合规，缺乏量化的环境目标和气候风险分析。"
    }

    EXAMPLE_MED = {
        "score": 60,
        "label": "60分 - 运营合规 (风险控制)",
        "file_path": "investor_y2/calib_60.pdf",
        "desc_short": "数据颗粒度高，缺乏前瞻战略",
        "desc_full": "ESG管理侧重于“运营合规”和“风险控制”，数据颗粒度很高（特别是排放数据），但缺乏宏大的ESG战略框架和气候变化风险的前瞻性布局。"
    }

    EXAMPLE_HIGH = {
        "score": 90,
        "label": "90分 - 战略融合 (深度赋能)",
        "file_path": "investor_y2/calib_90.pdf",
        "desc_short": "董事会治理，国际标准，供应链赋能",
        "desc_full": "ESG已经融入核心战略。特点是拥有完善的ESG治理架构（董事会层面），采用国际标准（ISO14064, UNGC, TCFD），关注气候变化风险、前沿技术创新以及供应链的深度ESG赋能。"
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    raw_text_access_count = models.IntegerField(initial=0)
    raw_pdf_open_count = models.IntegerField(initial=0)
    calibration_open_count = models.IntegerField(initial=0)
    report_new_window_click_count = models.IntegerField(initial=0)
    quick_prompt_click_count = models.IntegerField(initial=0)
    manual_prompt_send_count = models.IntegerField(initial=0)
    quick_prompt_send_count = models.IntegerField(initial=0)
    chat_send_count = models.IntegerField(initial=0)
    gpt_direct_score_prompt_count = models.IntegerField(initial=0)
    gpt_direct_score_extract_success = models.BooleanField(initial=False)
    gpt_direct_score = models.FloatField(null=True)
    gpt_direct_score_raw_reply = models.LongStringField(initial="")

    # --- 1. 投资者决策变量 ---
    estimated_score = models.IntegerField(
        min=0, max=100,
        label="基于您阅读的报告，请评估该公司的真实综合得分 (0-100分)"
    )

    # --- 2. 能力错觉 ---
    illusion_confidence = models.IntegerField(
        label="在不借助外部工具的情况下，您对自己评估该公司基本面的能力有多大信心？(0-100)",
        min=0, max=100
    )

    # --- 3. 客观理解测试 (Quiz) ---
    quiz_1 = models.IntegerField(
        label='本公司报告为哪个年度的报告？（请填写年份）'
    )
    quiz_2 = models.StringField(
        label='本公司本年度获得交易所哪个等级的评价？',
        choices=[
            ['A', '选项1：A或A+或A-'],
            ['B', '选项2：B或B+或B-'],
            ['C', '选项3：C或C+或C-'],
            ['D', '选项4：D或D+或D-'],
            ['E', '选项5：E或E+或E-'],
        ],
        widget=widgets.RadioSelect
    )
    quiz_3 = models.FloatField(
        label='本公司碳排放强度为多少（吨/万元营收）？（请填写数字）'
    )

    # --- 收益与系统变量 ---
    payoff_from_accuracy = models.CurrencyField(initial=0)
    payoff_from_quiz = models.CurrencyField(initial=0)
    seen_report_text = models.LongStringField()  # 存储 LaTeX 文本供记录
    chat_history = models.LongStringField(initial="")


# ================= PAGES =================

class WaitForManager(Page):
    """
    这是一个 '伪' 等待页。
    它不会拦住 Manager，但会拦住 Investor，直到 Manager 的数据就绪。
    """

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Investor'

    @staticmethod
    def live_method(player, data):
        # 前端发来 'check_status' 请求
        if data.get('type') == 'check_status':
            others = player.get_others_in_group()
            if others:
                manager = others[0]
                # 检查 Manager 是否打勾了 (注意区分 y1/y2/y3)
                is_ready = manager.participant.vars.get('manager_y2_done', False)

                if is_ready:
                    return {player.id_in_group: {'status': 'ready'}}
                else:
                    return {player.id_in_group: {'status': 'waiting'}}
            else:
                # 容错：如果没有队友
                return {player.id_in_group: {'status': 'ready'}}


class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Investor'

    @staticmethod
    def vars_for_template(player):
        treatment = str(player.participant.vars.get('treatment', 'Human'))
        env_map = {
            'AI': '智能辅助环境',
            'Human': '基础阅读环境',
            '100': '智能辅助环境',
            '0': '基础阅读环境',
        }
        return {
            'assigned_env_label': env_map.get(treatment, '当前分配环境')
        }


class CalibrationPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Investor'


class InvestorReading(Page):
    """阅读阶段：AI 辅助或直接阅读"""

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Investor'

    @staticmethod
    def vars_for_template(player):
        treatment = player.participant.vars.get('treatment', 'Human_Reader')

        # 获取 Manager 数据
        others = player.get_others_in_group()

        manager_text = "【数据等待中...】"
        pdf_url = ""

        if others:
            partner = others[0]
            # 1. 获取文本内容 (LaTeX源码)
            # 【关键修改】必须加 _y2 后缀
            manager_text = partner.participant.vars.get('final_report_text_y2', "Report content not found.")

            # 2. 获取参数以构建 PDF 路径
            # 【关键修改】必须加 _y2 后缀
            l = partner.participant.vars.get('final_linguistic_y2', 1)
            f = partner.participant.vars.get('final_format_y2', 1)
            p = partner.participant.vars.get('final_proximity_y2', 1)

            # 3. 构建 PDF URL
            # 【关键修改】静态文件夹指向 manager_y2
            manager_app_name = 'manager_y2'
            pdf_filename = f"{l}{f}{p}.pdf"
            pdf_url = f"/static/{manager_app_name}/reports_pdf/{pdf_filename}"

        player.seen_report_text = manager_text

        return {
            'treatment': treatment,
            'report_text': manager_text,
            'pdf_url': pdf_url,
            'calib_low': C.EXAMPLE_LOW,
            'calib_med': C.EXAMPLE_MED,
            'calib_high': C.EXAMPLE_HIGH
        }

    @staticmethod
    def live_method(player, data):
        msg_type = data.get('type')
        job_key = f"{C.NAME_IN_URL}:{player.participant.code}"

        if msg_type == 'log_access':
            player.raw_text_access_count += 1
            player.raw_pdf_open_count += 1
            return

        if msg_type == 'ui_event':
            event_name = data.get('event')
            if event_name == 'open_calibration_modal':
                player.calibration_open_count += 1
            elif event_name == 'open_raw_pdf':
                player.raw_pdf_open_count += 1
            elif event_name == 'open_report_new_window':
                player.report_new_window_click_count += 1
            elif event_name == 'click_quick_prompt':
                player.quick_prompt_click_count += 1
            return

        if msg_type == 'init_context':
            try:
                history = _load_chat_history(player)
                history = _ensure_system_message(player, history)
                history = _trim_history(history)
                _save_chat_history(player, history)
                return {
                    player.id_in_group: {
                        'init_ready': True,
                        'reply': '校准样本已加载（30/60/90分），可开始提问。'
                    }
                }
            except Exception as exc:
                print(f"[InvestorReading][INIT ERROR] participant={player.participant.code} error={exc}")
                print(traceback.format_exc())
                return {
                    player.id_in_group: {
                        'init_ready': False,
                        'error': str(exc)
                    }
                }

        if msg_type == 'chat_poll':
            with PENDING_CHAT_LOCK:
                job = PENDING_CHAT_JOBS.get(job_key)

            if not job:
                return {player.id_in_group: {'status': 'idle'}}

            future = job.get('future')
            if future is None:
                with PENDING_CHAT_LOCK:
                    PENDING_CHAT_JOBS.pop(job_key, None)
                return {player.id_in_group: {'status': 'idle'}}

            if not future.done():
                return {player.id_in_group: {'status': 'processing'}}

            with PENDING_CHAT_LOCK:
                PENDING_CHAT_JOBS.pop(job_key, None)

            try:
                assistant_reply = str(future.result()).strip()

                history = _load_chat_history(player)
                history = _ensure_system_message(player, history)
                history.append({'role': 'assistant', 'content': assistant_reply})
                history = _trim_history(history)
                _save_chat_history(player, history)

                prompt_id = job.get('prompt_id', '')
                extracted_score = None
                if prompt_id == 'direct_score_prompt':
                    player.gpt_direct_score_raw_reply = assistant_reply[:5000]
                    extracted_score = _extract_gpt_total_score(assistant_reply)
                    if extracted_score is not None:
                        player.gpt_direct_score = extracted_score
                        player.gpt_direct_score_extract_success = True
                    else:
                        player.gpt_direct_score_extract_success = False

                return {
                    player.id_in_group: {
                        'status': 'done',
                        'reply': assistant_reply,
                        'source': job.get('source', 'unknown'),
                        'prompt_id': prompt_id,
                        'gpt_score': extracted_score,
                    }
                }
            except Exception as exc:
                print(f"[InvestorReading][CHAT POLL ERROR] participant={player.participant.code} error={exc}")
                print(traceback.format_exc())
                return {
                    player.id_in_group: {
                        'status': 'done',
                        'reply': 'AI 服务暂时不可用，请稍后重试。',
                        'error': str(exc)
                    }
                }

        if msg_type == 'chat' or ('message' in data):
            user_msg = (data.get('prompt') or data.get('message') or '').strip()
            if not user_msg:
                return {player.id_in_group: {'reply': '请输入问题后再发送。'}}

            source = data.get('source', 'unknown')
            prompt_id = data.get('prompt_id', 'manual_prompt')
            player.chat_send_count += 1
            if source == 'quick_button':
                player.quick_prompt_send_count += 1
            else:
                player.manual_prompt_send_count += 1

            if prompt_id == 'direct_score_prompt':
                player.gpt_direct_score_prompt_count += 1

            with PENDING_CHAT_LOCK:
                existing = PENDING_CHAT_JOBS.get(job_key)
                if existing and existing.get('future') and not existing['future'].done():
                    return {
                        player.id_in_group: {
                            'status': 'processing',
                            'reply': 'AI 正在生成上一条回复，请稍候。'
                        }
                    }

            try:
                history = _load_chat_history(player)
                history = _ensure_system_message(player, history)
                history.append({'role': 'user', 'content': user_msg})
                history = _trim_history(history)
                _save_chat_history(player, history)

                future = CHAT_EXECUTOR.submit(_call_openai_compatible, history)
                with PENDING_CHAT_LOCK:
                    PENDING_CHAT_JOBS[job_key] = {
                        'future': future,
                        'source': source,
                        'prompt_id': prompt_id,
                        'submitted_at': time.time(),
                    }

                return {
                    player.id_in_group: {
                        'status': 'processing',
                        'poll_after': CHAT_POLL_INTERVAL_SECONDS,
                        'source': source,
                        'prompt_id': prompt_id,
                    }
                }
            except Exception as exc:
                print(f"[InvestorReading][CHAT ENQUEUE ERROR] participant={player.participant.code} error={exc}")
                print(traceback.format_exc())
                return {
                    player.id_in_group: {
                        'status': 'done',
                        'reply': 'AI 服务暂时不可用，请稍后重试。',
                        'error': str(exc)
                    }
                }


class InvestmentDecision(Page):
    """决策阶段：打分与投资"""
    form_model = 'player'
    form_fields = ['estimated_score', 'illusion_confidence']

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Investor'


class ComprehensionQuiz(Page):
    form_model = 'player'
    form_fields = ['quiz_1', 'quiz_2', 'quiz_3']

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Investor'

    @staticmethod
    def before_next_page(player, timeout_happened):
        # 1. 计算 Investor 本轮收益
        diff = abs(player.estimated_score - C.TRUE_COMPANY_VALUE)
        acc_pay = max(0, C.MAX_ACCURACY_PAYOFF - diff * C.PENALTY_PER_POINT)

        quiz_pts = 0
        if player.quiz_1 == 2024:
            quiz_pts += 1
        if player.quiz_2 == 'A':
            quiz_pts += 1
        if player.quiz_3 is not None and 0 <= float(player.quiz_3) <= 1:
            quiz_pts += 1
        q_pay = quiz_pts * C.QUIZ_BONUS

        inv_total = acc_pay + q_pay

        # ==========================================================
        # 【关键修改】存储 Investor 变量 (增加 _y2 后缀)
        # ==========================================================
        player.participant.vars['investpayoff_y2'] = float(inv_total)

        player.participant.vars['inv_accuracy_pay_y2'] = float(acc_pay)
        player.participant.vars['inv_quiz_pay_y2'] = float(q_pay)
        player.participant.vars['inv_true_val_y2'] = C.TRUE_COMPANY_VALUE
        player.participant.vars['inv_est_val_y2'] = player.estimated_score
        player.participant.vars['inv_report_open_count_y2'] = int(player.raw_pdf_open_count)
        player.participant.vars['inv_calibration_open_count_y2'] = int(player.calibration_open_count)
        player.participant.vars['inv_report_new_window_click_count_y2'] = int(player.report_new_window_click_count)
        player.participant.vars['inv_quick_prompt_click_count_y2'] = int(player.quick_prompt_click_count)
        player.participant.vars['inv_manual_prompt_send_count_y2'] = int(player.manual_prompt_send_count)
        player.participant.vars['inv_quick_prompt_send_count_y2'] = int(player.quick_prompt_send_count)
        player.participant.vars['inv_chat_send_count_y2'] = int(player.chat_send_count)
        player.participant.vars['inv_gpt_direct_score_prompt_count_y2'] = int(player.gpt_direct_score_prompt_count)
        player.participant.vars['inv_gpt_direct_score_extract_success_y2'] = bool(player.gpt_direct_score_extract_success)
        player.participant.vars['inv_gpt_direct_score_y2'] = player.field_maybe_none('gpt_direct_score')

        # ==========================================================
        # 【关键修改】存储 Manager 变量 (增加 _y2 后缀)
        # ==========================================================
        others = player.get_others_in_group()
        if others:
            manager = others[0]
            investor_rating = player.estimated_score
            manager_game_payoff = float(C.MANAGER_BASE_PAY) + (C.MANAGER_RETURN_RATE * investor_rating)

            # 存入 Manager 的 participant.vars
            manager.participant.vars['investpayoff_y2'] = manager_game_payoff

            # 存储细节
            manager.participant.vars['mgr_score_y2'] = investor_rating
            manager.participant.vars['mgr_base_y2'] = float(C.MANAGER_BASE_PAY)
            manager.participant.vars['mgr_bonus_y2'] = float(C.MANAGER_RETURN_RATE * investor_rating)


page_sequence = [
    WaitForManager, Introduction, CalibrationPage, InvestorReading,
    InvestmentDecision, ComprehensionQuiz
]