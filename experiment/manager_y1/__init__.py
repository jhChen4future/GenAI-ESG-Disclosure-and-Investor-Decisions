from otree.api import *
import math
import random
import os
import time

doc = """
管理者任务 (Round 1)：策略法 (Strategy Method)。
管理者需针对对手拥有AI辅助的概率（0%, 50%, 100%）分别制定披露策略。
本轮数据存储在标准变量中（无后缀），供 Investor_y1 读取。
"""


class C(BaseConstants):
    NAME_IN_URL = 'manager_y1'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    # [A] 文本易读性 (Linguistic)
    LINGUISTIC = [
        (1, 'L1 - 通俗易懂'),
        (2, 'L2 - 标准专业'),
        (3, 'L3 - 晦涩学术')
    ]

    # [B] 视觉格式 (Format)
    FORMAT = [
        (1, 'L1 - 高结构化（易于阅读）'),
        (2, 'L2 - 标准段落（常规阅读）'),
        (3, 'L3 - 文本堆砌（难以阅读）')
    ]

    # [C] 披露策略 (Proximity) - 固定为 2 (实质性)
    FIXED_PROXIMITY = 2

    @staticmethod
    def get_report_data(l, f):
        # 使用固定的 P
        p = C.FIXED_PROXIMITY

        # 1. 构造文件名 (例如 "121")
        filename = f"{l}{f}{p}"

        # 2. APP 文件夹名字
        app_name = 'manager_y1'

        # 3. 构造 PDF 的 URL
        pdf_url = f"/static/{app_name}/reports_pdf/{filename}.pdf"

        # 4. 读取 Tex 源码
        base_path = os.path.dirname(os.path.abspath(__file__))
        tex_path = os.path.join(base_path, 'report_sources', f"{filename}.tex")

        latex_content = f"【系统错误】未找到源文件: {filename}.tex"

        if os.path.exists(tex_path):
            try:
                with open(tex_path, 'r', encoding='utf-8') as f_obj:
                    latex_content = f_obj.read()
            except Exception as e:
                latex_content = f"读取错误: {str(e)}"

        return latex_content, pdf_url


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # 存储最终生效的报告
    final_report_text = models.LongStringField()
    final_linguistic = models.IntegerField()
    final_format = models.IntegerField()
    final_proximity = models.IntegerField()


class Player(BasePlayer):
    # --- 策略法决策字段 ---

    # 场景 1: 对手 0% 可能有 AI (即 Human)
    strat_0_l = models.IntegerField(label="0% AI 概率 - 语言")
    strat_0_f = models.IntegerField(label="0% AI 概率 - 格式")

    # 场景 2: 对手 25% 可能有 AI
    strat_25_l = models.IntegerField(label="25% AI 概率 - 语言")
    strat_25_f = models.IntegerField(label="25% AI 概率 - 格式")

    # 场景 3: 对手 50% 可能有 AI
    strat_50_l = models.IntegerField(label="50% AI 概率 - 语言")
    strat_50_f = models.IntegerField(label="50% AI 概率 - 格式")

    # 场景 4: 对手 75% 可能有 AI
    strat_75_l = models.IntegerField(label="75% AI 概率 - 语言")
    strat_75_f = models.IntegerField(label="75% AI 概率 - 格式")

    # 场景 5: 对手 100% 可能有 AI (即 AI Agent)
    strat_100_l = models.IntegerField(label="100% AI 概率 - 语言")
    strat_100_f = models.IntegerField(label="100% AI 概率 - 格式")

    # 记录实际应用了哪个场景
    applied_scenario = models.StringField()
    strategy_form_seconds = models.FloatField(initial=0)


# --- 分组与身份分配逻辑 (仅在第一轮 y1 执行) ---
def set_treatment(subsession: Subsession):
    groups = subsession.get_groups()
    num_groups = len(groups)

    # 简单的随机分配：一半组是 AI，一半组是 Human
    num_ai = math.ceil(num_groups / 2)
    treatments = ['AI'] * num_ai + ['Human'] * (num_groups - num_ai)
    random.shuffle(treatments)

    for i, group in enumerate(groups):
        assigned_treatment = treatments[i]
        p1 = group.get_player_by_id(1)
        p2 = group.get_player_by_id(2)

        # 将角色和 Treatment 写入 participant.vars，贯穿整个实验
        p1.participant.vars['role'] = 'Manager'
        p1.participant.vars['treatment'] = assigned_treatment

        p2.participant.vars['role'] = 'Investor'
        p2.participant.vars['treatment'] = assigned_treatment


# =============================================================================
# PAGES
# =============================================================================

class IdentityInitiate(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = set_treatment


class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Manager'


class Manager(Page):
    form_model = 'player'
    # 前端需要提交这6个字段
    form_fields = [
        'strat_0_l', 'strat_0_f',
        'strat_25_l', 'strat_25_f',
        'strat_50_l', 'strat_50_f',
        'strat_75_l', 'strat_75_f',
        'strat_100_l', 'strat_100_f'
    ]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Manager'

    @staticmethod
    def vars_for_template(player):
        player.participant.vars['manager_strategy_start_ts_y1'] = time.time()
        grid_items = []
        for l_val, l_label in C.LINGUISTIC:
            row_items = []
            for f_val, f_label in C.FORMAT:
                _, url = C.get_report_data(l_val, f_val)
                row_items.append({
                    'l': l_val,
                    'f': f_val,
                    'label_short': f"L{l_val}-F{f_val}",
                    'desc': f"{l_label} + {f_label}",
                    'pdf_url': url
                })
            # 【关键修改】使用 'cols' 避免与 Python 字典的 .items() 方法冲突
            grid_items.append({'l_label': l_label, 'cols': row_items})

        return {
            'grid_items': grid_items
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.participant.vars.get('role') == 'Manager':
            started_at = player.participant.vars.get('manager_strategy_start_ts_y1')
            if started_at is not None:
                player.strategy_form_seconds = max(0, time.time() - float(started_at))
                player.participant.vars['manager_strategy_form_seconds_y1'] = player.strategy_form_seconds

            # 1. 获取该组的真实 Treatment (AI 或 Human)
            treatment = player.participant.vars.get('treatment', 'Human')

            # 2. 根据 Treatment 匹配策略（兼容当前 AI/Human 与未来 0/25/50/75/100）
            scenario_key = '0'
            if treatment == 'AI':
                scenario_key = '100'
            elif treatment == 'Human':
                scenario_key = '0'
            elif str(treatment) in ['0', '25', '50', '75', '100']:
                scenario_key = str(treatment)

            scenario_map = {
                '0': (player.strat_0_l, player.strat_0_f),
                '25': (player.strat_25_l, player.strat_25_f),
                '50': (player.strat_50_l, player.strat_50_f),
                '75': (player.strat_75_l, player.strat_75_f),
                '100': (player.strat_100_l, player.strat_100_f),
            }
            selected_l, selected_f = scenario_map.get(scenario_key, (player.strat_0_l, player.strat_0_f))
            player.applied_scenario = f"{scenario_key}%"

            selected_p = C.FIXED_PROXIMITY

            # 3. 生成最终报告源码
            final_latex, final_pdf = C.get_report_data(selected_l, selected_f)

            # 4. 存入数据库 (Group)
            player.group.final_report_text = final_latex
            player.group.final_linguistic = selected_l
            player.group.final_format = selected_f
            player.group.final_proximity = selected_p

            # 5. 存入 Session 变量 (供 Investor 读取)
            # 注意：manager_y1 使用默认键名 (无后缀)，因为 investor_y1 默认读取这些键
            player.participant.vars['final_report_text'] = final_latex
            player.participant.vars['final_linguistic'] = selected_l
            player.participant.vars['final_format'] = selected_f
            player.participant.vars['final_proximity'] = selected_p
            player.participant.vars['manager_y1_done'] = True



page_sequence = [IdentityInitiate, Introduction, Manager]