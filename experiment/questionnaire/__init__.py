from otree.api import *
import random

doc = """
Final Questionnaire
围绕 AI 辅助决策中的认知负荷、信任与依赖、操纵感知、能力校准、责任归因与决策质量进行结构化测量。
"""


class C(BaseConstants):
    NAME_IN_URL = 'final_survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    SHOWUP_FEE = 5
    MANAGER_TASK_A_POINTS_PER_RMB = 2.5
    INVESTOR_TASK_A_POINTS_PER_RMB = 2.0

    LIKERT_7 = [
        [1, '1 - 非常不同意'],
        [2, '2 - 不同意'],
        [3, '3 - 有点不同意'],
        [4, '4 - 中立'],
        [5, '5 - 有点同意'],
        [6, '6 - 同意'],
        [7, '7 - 非常同意'],
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # --- 1. 人口统计学 ---
    age = models.IntegerField(label='您的年龄', min=16, max=100)
    gender = models.StringField(
        choices=[['男性', '男性'], ['女性', '女性']],
        label='您的性别',
        widget=widgets.RadioSelect
    )
    major = models.StringField(label='您的在读专业')
    grade = models.StringField(
        choices=[
            ['大一', '大一'], ['大二', '大二'], ['大三', '大三'], ['大四', '大四'], ['大五', '大五'],
            ['硕士一年级', '硕士一年级'], ['硕士二年级', '硕士二年级'], ['硕士三年级', '硕士三年级'],
            ['直博一年级', '直博一年级'], ['直博二年级', '直博二年级'],
            ['直博三年级（含硕转博一年级）', '直博三年级（含硕转博一年级）'],
            ['直博四年级', '直博四年级'], ['直博五年级', '直博五年级'], ['直博六年级', '直博六年级'],
            ['其他', '其他']
        ],
        label='您所在的年级',
        widget=widgets.RadioSelect
    )
    GPT = models.StringField(
        choices=[
            ['极少使用（少于每月一次）', '极少使用（少于每月一次）'],
            ['每月至少一次', '每月至少一次'],
            ['每周至少一次', '每周至少一次'],
            ['每周至少三次', '每周至少三次'],
            ['每天至少一次', '每天至少一次']
        ],
        label='您的GPT大模型（ChatGPT、Claude、Kimi、文心一言等）使用频率（说明：“每天至少一次”指当天使用过GPT即可，无论当天使用多少次，均按1次计）',
        widget=widgets.RadioSelect
    )

    major_background = models.IntegerField(
        label="您的专业背景是否属于经济、金融、会计或管理类？",
        choices=[[1, "是 (商科背景)"], [0, "否 (非商科背景)"]],
        widget=widgets.RadioSelect
    )

    investment_exp = models.IntegerField(
        label="您的个人股票/基金投资经验：",
        choices=[[1, "无经验"], [2, "少于1年"], [3, "1-3年"], [4, "3年以上"]],
        widget=widgets.RadioSelect
    )

    risk_preference = models.IntegerField(
        label="总体而言，您认为自己是一个愿意承担风险的人吗？(0-10)",
        choices=range(0, 11),
        widget=widgets.RadioSelectHorizontal
    )

    # --- 2. 机制问卷（7点评分）---
    # 维度A：认知负荷与处理难度
    cognitive_effort = models.IntegerField(
        choices=C.LIKERT_7,
        label="1. 在阅读报告并做出估值的过程中，我感到认知负荷较高（如记忆与整合信息较费力）。",
        widget=widgets.RadioSelect
    )
    information_overload = models.IntegerField(
        choices=C.LIKERT_7,
        label="2. 报告中的信息量较大，使我在筛选关键线索时感到压力。",
        widget=widgets.RadioSelect
    )

    # 维度B：操纵感知与框架影响
    perceived_manipulation = models.IntegerField(
        choices=C.LIKERT_7,
        label="3. 我感觉这份报告的呈现方式可能在引导我的判断方向。",
        widget=widgets.RadioSelect
    )
    framing_bias = models.IntegerField(
        choices=C.LIKERT_7,
        label="4. 报告的措辞与结构显著影响了我对公司基本面的评价。",
        widget=widgets.RadioSelect
    )

    # 维度C：AI信任与依赖
    ai_trust = models.IntegerField(
        choices=C.LIKERT_7,
        label="5. 我认为该 AI 助手提供的信息总体上是可靠的。",
        widget=widgets.RadioSelect
    )
    ai_reliance = models.IntegerField(
        choices=C.LIKERT_7,
        label="6. 在做出最终决定时，我在较大程度上参考了 AI 的分析。",
        widget=widgets.RadioSelect
    )
    ai_dependence = models.IntegerField(
        choices=C.LIKERT_7,
        label="7. 如果没有 AI 辅助，我对自己完成同等质量判断的把握会明显下降。",
        widget=widgets.RadioSelect
    )

    # 维度D：能力错觉与校准
    ai_illusion = models.IntegerField(
        choices=C.LIKERT_7,
        label="8. 使用 AI 让我产生了“自己已充分理解公司”的感觉。",
        widget=widgets.RadioSelect
    )
    ai_mislead = models.IntegerField(
        choices=C.LIKERT_7,
        label="9. 我认为 AI 输出中可能包含不完整或误导性信息。",
        widget=widgets.RadioSelect
    )
    confidence_calibration = models.IntegerField(
        choices=C.LIKERT_7,
        label="10. 回顾本次任务，我对自己判断准确性的信心与实际表现大体一致。",
        widget=widgets.RadioSelect
    )

    # 维度E：归因与决策结果评估
    attribution_error = models.IntegerField(
        choices=C.LIKERT_7,
        label="11. 若决策结果不佳，我更倾向于归因于外部信息质量，而非自身判断过程。",
        widget=widgets.RadioSelect
    )
    decision_accountability = models.IntegerField(
        choices=C.LIKERT_7,
        label="12. 即使参考了 AI 建议，我仍认为最终决策责任主要由我本人承担。",
        widget=widgets.RadioSelect
    )
    perceived_decision_quality = models.IntegerField(
        choices=C.LIKERT_7,
        label="13. 综合来看，我认为自己本次做出的投资判断质量较高。",
        widget=widgets.RadioSelect
    )

    # 维度F：Prompt 工程与人机交互策略
    prompt_engineering_use = models.IntegerField(
        choices=C.LIKERT_7,
        label="14. 在与 AI 交互时，我会有意识地优化提问方式（如限定角色、任务、输出格式）以提升回答质量。",
        widget=widgets.RadioSelect
    )
    prompt_iteration = models.IntegerField(
        choices=C.LIKERT_7,
        label="15. 为获得更有用的信息，我通常会多轮迭代修改提示词，而不是只提一次问题。",
        widget=widgets.RadioSelect
    )
    prompt_specificity = models.IntegerField(
        choices=C.LIKERT_7,
        label="16. 相比笼统提问，我更倾向于给 AI 提供具体约束（如比较维度、评分口径、证据要求）。",
        widget=widgets.RadioSelect
    )

    # 维度G：管理者对 AI 对手的策略适配（非管理者可按感受作答）
    ai_counterstrategy_intent = models.IntegerField(
        choices=C.LIKERT_7,
        label="17. 我会根据对方是否可能使用 AI，调整信息呈现策略以影响其判断结果。",
        widget=widgets.RadioSelect
    )
    ai_detectability_belief = models.IntegerField(
        choices=C.LIKERT_7,
        label="18. 我认为 AI 比人类更容易识别文本中的操纵性线索，因此需要采用不同的信息策略。",
        widget=widgets.RadioSelect
    )
    human_ai_differentiation = models.IntegerField(
        choices=C.LIKERT_7,
        label="19. 在本实验中，我对“面向人类”与“面向 AI”对象的报告参数选择确实存在系统性差异。",
        widget=widgets.RadioSelect
    )

    # --- 3. 支付记录 ---
    payoff_task_y1 = models.CurrencyField(initial=0)
    payoff_task_y2 = models.CurrencyField(initial=0)
    payoff_task_y3 = models.CurrencyField(initial=0)
    payoff_svo = models.CurrencyField(initial=0)
    selected_round = models.StringField(initial='')
    selected_round_task_payoff = models.CurrencyField(initial=0)
    payoff_from_experiment = models.CurrencyField()
    total_final_payoff = models.CurrencyField()
    suggestion = models.LongStringField(label='您的建议')

# =============================================================================
# PAGES
# =============================================================================

class WaitForAll(WaitPage):
    title_text = "请稍候"
    body_text = "正在等待所有参与者完成实验任务..."
    wait_for_all_groups = True


class MechanismSurvey(Page):
    form_model = 'player'
    form_fields = [
        'cognitive_effort', 'information_overload',
        'perceived_manipulation', 'framing_bias',
        'ai_trust', 'ai_reliance', 'ai_dependence',
        'ai_illusion', 'ai_mislead', 'confidence_calibration',
        'attribution_error', 'decision_accountability', 'perceived_decision_quality',
        'prompt_engineering_use', 'prompt_iteration', 'prompt_specificity',
        'ai_counterstrategy_intent', 'ai_detectability_belief', 'human_ai_differentiation'
    ]


class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age', 'gender', 'major', 'grade',
        'major_background', 'investment_exp', 'GPT',
        'risk_preference'
    ]


class Suggestion(Page):
    form_model = 'player'
    form_fields = ['suggestion']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        p_vars = player.participant.vars
        rounds = ['y1', 'y2', 'y3']
        role = p_vars.get('role')
        participant_code = player.participant.code

        def as_float(value, default=0.0):
            if value is None:
                return float(default)
            try:
                return float(value)
            except Exception:
                return float(default)

        available_rounds = [r for r in rounds if p_vars.get(f'investpayoff_{r}') is not None]

        if role == 'Investor':
            detail_rounds = [
                r for r in rounds
                if p_vars.get(f'inv_true_val_{r}') is not None and p_vars.get(f'inv_est_val_{r}') is not None
            ]
        elif role == 'Manager':
            detail_rounds = [
                r for r in rounds
                if p_vars.get(f'mgr_base_{r}') is not None and p_vars.get(f'mgr_bonus_{r}') is not None
            ]
        else:
            detail_rounds = []

        candidate_rounds = [r for r in available_rounds if r in detail_rounds]
        if candidate_rounds:
            selected_round = random.choice(candidate_rounds)
        elif available_rounds:
            selected_round = random.choice(available_rounds)
        else:
            selected_round = 'y1'

        player.participant.vars['selected_round_name'] = selected_round

        task_a_points = as_float(p_vars.get(f'investpayoff_{selected_round}'), 0)
        svo_val = as_float(p_vars.get('svopayoff'), 0)

        y1_points = as_float(p_vars.get('investpayoff_y1'), 0)
        y2_points = as_float(p_vars.get('investpayoff_y2'), 0)
        y3_points = as_float(p_vars.get('investpayoff_y3'), 0)

        task_a_points_per_rmb = (
            float(C.MANAGER_TASK_A_POINTS_PER_RMB)
            if role == 'Manager'
            else float(C.INVESTOR_TASK_A_POINTS_PER_RMB)
        )

        task_a_money = task_a_points / task_a_points_per_rmb
        y1_money = y1_points / task_a_points_per_rmb
        y2_money = y2_points / task_a_points_per_rmb
        y3_money = y3_points / task_a_points_per_rmb

        total_val = task_a_money + svo_val + float(C.SHOWUP_FEE)

        player.payoff_task_y1 = cu(y1_money)
        player.payoff_task_y2 = cu(y2_money)
        player.payoff_task_y3 = cu(y3_money)
        player.payoff_svo = cu(svo_val)
        player.selected_round = selected_round
        player.selected_round_task_payoff = cu(task_a_money)

        player.payoff_from_experiment = cu(task_a_money + svo_val)
        player.total_final_payoff = cu(total_val)
        player.payoff = player.total_final_payoff

        def hoist_with_fallback(target_key, base_key):
            value = p_vars.get(f'{base_key}_{selected_round}')
            if value is None:
                for r in rounds:
                    alt = p_vars.get(f'{base_key}_{r}')
                    if alt is not None:
                        value = alt
                        break
            p_vars[target_key] = value

        if role == 'Investor':
            hoist_with_fallback('final_inv_accuracy', 'inv_accuracy_pay')
            hoist_with_fallback('final_inv_quiz', 'inv_quiz_pay')
            hoist_with_fallback('final_inv_true', 'inv_true_val')
            hoist_with_fallback('final_inv_est', 'inv_est_val')

        elif role == 'Manager':
            hoist_with_fallback('final_mgr_score', 'mgr_score')
            hoist_with_fallback('final_mgr_base', 'mgr_base')
            hoist_with_fallback('final_mgr_bonus', 'mgr_bonus')

            if p_vars.get('final_mgr_base') is None:
                p_vars['final_mgr_base'] = 10.0
            if p_vars.get('final_mgr_bonus') is None:
                p_vars['final_mgr_bonus'] = round(max(0.0, task_a_points - 10.0), 4)
            if p_vars.get('final_mgr_score') is None:
                p_vars['final_mgr_score'] = round(max(0.0, (task_a_points - 10.0) / 0.5), 4)

        debug_round_snapshot = {
            r: {
                'investpayoff': p_vars.get(f'investpayoff_{r}'),
                'inv_true': p_vars.get(f'inv_true_val_{r}'),
                'inv_est': p_vars.get(f'inv_est_val_{r}'),
                'mgr_score': p_vars.get(f'mgr_score_{r}'),
                'mgr_base': p_vars.get(f'mgr_base_{r}'),
                'mgr_bonus': p_vars.get(f'mgr_bonus_{r}'),
            }
            for r in rounds
        }

        print(f"[FINAL_PAYOFF_DEBUG] participant={participant_code} role={role}")
        print(f"[FINAL_PAYOFF_DEBUG] selected_round={selected_round} available_rounds={available_rounds} detail_rounds={detail_rounds}")
        print(f"[FINAL_PAYOFF_DEBUG] task_a_points={task_a_points} task_a_money={task_a_money} svo={svo_val} total={total_val}")
        print(f"[FINAL_PAYOFF_DEBUG] round_snapshot={debug_round_snapshot}")
        key_dump = {
            k: p_vars.get(k)
            for k in sorted(p_vars.keys())
            if k.startswith('investpayoff_') or k.startswith('inv_') or k.startswith('mgr_') or k in ['role', 'treatment', 'svopayoff']
        }
        print(f"[FINAL_PAYOFF_DEBUG] key_dump={key_dump}")


class End(Page):
    @staticmethod
    def vars_for_template(player: Player):
        p_vars = player.participant.vars
        rounds = ['y1', 'y2', 'y3']

        def pick_with_round_fallback(base_key, selected_round):
            val = p_vars.get(f'{base_key}_{selected_round}')
            if val is not None:
                return val
            for r in rounds:
                alt = p_vars.get(f'{base_key}_{r}')
                if alt is not None:
                    return alt
            return p_vars.get(base_key)

        role = p_vars.get('role', 'Unknown')
        round_name = p_vars.get('selected_round_name', 'y1')
        round_display = {'y1': '第一轮', 'y2': '第二轮', 'y3': '第三轮'}.get(round_name, round_name)

        task_a_points_per_rmb = (
            float(C.MANAGER_TASK_A_POINTS_PER_RMB)
            if role == 'Manager'
            else float(C.INVESTOR_TASK_A_POINTS_PER_RMB)
        )
        task_a_rmb_per_point = 1.0 / task_a_points_per_rmb

        total_val = float(player.total_final_payoff) if player.total_final_payoff is not None else 0.0
        svo_val = p_vars.get('svopayoff')
        svo_float = float(svo_val) if svo_val is not None else 0.0
        invest_val = float(player.selected_round_task_payoff) if player.selected_round_task_payoff is not None else 0.0

        data = {
            'role': role,
            'selected_round_display': round_display,
            'exchange_rate_str': f"任务A按 1点={task_a_rmb_per_point:.2f}人民币结算；任务B(SVO)按 1点=0.05人民币结算",
            'svo_payoff_str': f"{svo_float:.1f} 元",
            'invest_task_total_str': f"{invest_val:.1f} 元",
            'showup_fee_str': f"{float(C.SHOWUP_FEE):.1f} 元",
            'total_payoff_str': f"{total_val:.1f} 元",
            'payoff_y1_str': f"{float(player.payoff_task_y1):.1f} 元",
            'payoff_y2_str': f"{float(player.payoff_task_y2):.1f} 元",
            'payoff_y3_str': f"{float(player.payoff_task_y3):.1f} 元",
            'selected_round_task_payoff_str': f"{float(player.selected_round_task_payoff):.1f} 元"
        }

        if role == 'Investor':
            true_val = p_vars.get('final_inv_true')
            est_val = p_vars.get('final_inv_est')
            inv_accuracy = p_vars.get('final_inv_accuracy')
            inv_quiz = p_vars.get('final_inv_quiz')

            if true_val is None:
                true_val = pick_with_round_fallback('inv_true_val', round_name)
            if est_val is None:
                est_val = pick_with_round_fallback('inv_est_val', round_name)
            if inv_accuracy is None:
                inv_accuracy = pick_with_round_fallback('inv_accuracy_pay', round_name)
            if inv_quiz is None:
                inv_quiz = pick_with_round_fallback('inv_quiz_pay', round_name)

            diff = "N/A"
            if true_val is not None and est_val is not None:
                try:
                    diff = abs(float(true_val) - float(est_val))
                except Exception:
                    diff = "N/A"

            missing = []
            if true_val is None:
                missing.append('inv_true_val')
            if est_val is None:
                missing.append('inv_est_val')
            if inv_accuracy is None:
                missing.append('inv_accuracy_pay')
            if inv_quiz is None:
                missing.append('inv_quiz_pay')

            data.update({
                'inv_accuracy_str': str(inv_accuracy) if inv_accuracy is not None else '--',
                'inv_quiz_str': str(inv_quiz) if inv_quiz is not None else '--',
                'true_val': true_val,
                'est_val': est_val,
                'diff': diff,
                'inv_detail_missing': len(missing) > 0,
                'inv_detail_missing_msg': '缺失键: ' + ', '.join(missing) if missing else ''
            })

        elif role == 'Manager':
            mgr_score = p_vars.get('final_mgr_score')
            mgr_base = p_vars.get('final_mgr_base')
            mgr_bonus = p_vars.get('final_mgr_bonus')

            if mgr_score is None:
                mgr_score = pick_with_round_fallback('mgr_score', round_name)
            if mgr_base is None:
                mgr_base = pick_with_round_fallback('mgr_base', round_name)
            if mgr_bonus is None:
                mgr_bonus = pick_with_round_fallback('mgr_bonus', round_name)

            invest_points_selected = pick_with_round_fallback('investpayoff', round_name)
            invest_points_selected = float(invest_points_selected) if invest_points_selected is not None else None

            if mgr_base is None and invest_points_selected is not None:
                mgr_base = 10.0
            if mgr_bonus is None and invest_points_selected is not None:
                mgr_bonus = round(max(0.0, invest_points_selected - 10.0), 4)
            if mgr_score is None and invest_points_selected is not None:
                mgr_score = round(max(0.0, (invest_points_selected - 10.0) / 0.5), 4)

            missing = []
            if mgr_score is None:
                missing.append('mgr_score')
            if mgr_base is None:
                missing.append('mgr_base')
            if mgr_bonus is None:
                missing.append('mgr_bonus')

            mgr_base_points = float(mgr_base) if mgr_base is not None else None
            mgr_bonus_points = float(mgr_bonus) if mgr_bonus is not None else None
            mgr_base_money = (
                mgr_base_points / task_a_points_per_rmb
                if mgr_base_points is not None else None
            )
            mgr_bonus_money = (
                mgr_bonus_points / task_a_points_per_rmb
                if mgr_bonus_points is not None else None
            )

            data.update({
                'mgr_received_score': mgr_score,
                'mgr_base_str': (
                    f"{mgr_base_money:.1f} 元（{mgr_base_points:.1f} 点）"
                    if mgr_base_points is not None else '--'
                ),
                'mgr_bonus_str': (
                    f"{mgr_bonus_money:.1f} 元（{mgr_bonus_points:.1f} 点）"
                    if mgr_bonus_points is not None else '--'
                ),
                'mgr_detail_missing': len(missing) > 0,
                'mgr_detail_missing_msg': '缺失键: ' + ', '.join(missing) if missing else ''
            })

        return data


page_sequence = [WaitForAll, MechanismSurvey, Demographics, Suggestion, End]