from otree.api import *
import math
import random
import os
import time

doc = """
管理者任务 (Round 2)：策略法 (Strategy Method)。
逻辑与 Y1 相同，但数据存储在 _y2 后缀变量中，且每轮重新随机匹配对手。
"""


class C(BaseConstants):
    NAME_IN_URL = 'manager_y2' # 【修改】App 名称
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    # [A] 文本易读性 (Linguistic)
    LINGUISTIC = [
        (1, '文本语言1 - 通俗易懂'),
        (2, '文本语言2 - 标准专业'),
        (3, '文本语言3 - 晦涩学术')
    ]

    # [B] 视觉格式 (Format)
    FORMAT = [
        (1, '文本格式1 - 高结构化（易于阅读）'),
        (2, '文本格式2 - 标准段落（常规阅读）'),
        (3, '文本格式3 - 文本堆砌（难以阅读）')
    ]

    # [C] 披露策略 固定为 2 (实质性)
    FIXED_PROXIMITY = 2

    @staticmethod
    def get_report_data(l, f):
        # 使用固定的 P
        p = C.FIXED_PROXIMITY

        # 1. 构造文件名
        filename = f"{l}{f}{p}"

        # 2. 【修改】指向 y2 的静态文件夹
        app_name = 'manager_y2'

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
    def creating_session(subsession):
        # 【修改】重新匹配
        # fixed_id_in_group=True 保证了 P1(Manager) 还是 P1，P2(Investor) 还是 P2
        # 只是把不同的 P1 和 P2 组合在一起
        subsession.group_randomly(fixed_id_in_group=True)


class Group(BaseGroup):
    # 存储最终生效的报告（数据库字段无需加后缀，因为这是 y2 独立的表）
    final_report_text = models.LongStringField()
    final_linguistic = models.IntegerField()
    final_format = models.IntegerField()
    final_proximity = models.IntegerField()


class Player(BasePlayer):
    # --- 策略法决策字段 ---
    # 同样，数据库字段无需改名，因为这是 manager_y2 独立的数据表

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


# =============================================================================
# PAGES
# =============================================================================

class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        # 角色已经存储在 participant.vars 中，直接读取即可
        return player.participant.vars.get('role') == 'Manager'


class Manager(Page):
    form_model = 'player'
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
        player.participant.vars['manager_strategy_start_ts_y2'] = time.time()
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
            # 保持使用 cols
            grid_items.append({'l_label': l_label, 'cols': row_items})

        return {
            'grid_items': grid_items
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.participant.vars.get('role') == 'Manager':
            started_at = player.participant.vars.get('manager_strategy_start_ts_y2')
            if started_at is not None:
                player.strategy_form_seconds = max(0, time.time() - float(started_at))
                player.participant.vars['manager_strategy_form_seconds_y2'] = player.strategy_form_seconds

            # 1. 获取 Treatment (从 y1 继承)
            treatment = player.participant.vars.get('treatment', 'Human')

            # 2. 匹配策略（兼容当前 AI/Human 与未来 0/25/50/75/100）
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

            # 3. 生成报告源码
            final_latex, final_pdf = C.get_report_data(selected_l, selected_f)

            # 4. 存入数据库 (本轮独立数据)
            player.group.final_report_text = final_latex
            player.group.final_linguistic = selected_l
            player.group.final_format = selected_f
            player.group.final_proximity = selected_p

            # 5. 【核心修改】存入 participant.vars (使用 _y2 后缀)
            # 这样 Investor_y2 才能读到正确的数据，且不覆盖 y1
            player.participant.vars['final_report_text_y2'] = final_latex
            player.participant.vars['final_linguistic_y2'] = selected_l
            player.participant.vars['final_format_y2'] = selected_f
            player.participant.vars['final_proximity_y2'] = selected_p
            player.participant.vars['manager_y2_done'] = True


page_sequence = [Introduction, Manager]