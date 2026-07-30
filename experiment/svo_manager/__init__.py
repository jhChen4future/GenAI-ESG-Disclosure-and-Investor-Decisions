from otree.api import *
import random  # 【关键】必须导入随机库

doc = """
SVO (Social Value Orientation) 任务
包含 15 个决策矩阵。
收益计算规则：随机抽取 1 个回合，根据玩家选择的 (Self, Other) 分配，
计算 Self 部分乘以系数后的金额作为 payoff。
"""


class C(BaseConstants):
    NAME_IN_URL = 'manager_svo'  # 如果是 manager 请改为 manager_svo
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    # === SVO 收益转换系数 ===
    # 当前设置：点数 * 0.05 = 实际金额
    CONVERSION_FACTOR = 0.05

    # === 15个题目的矩阵数据 (直接使用您提供的数据) ===
    # 结构：List[List[Tuple(Self, Other)]]
    SVO_MATRICES = [
        # --- 第 1 题 ---
        [(85, 85), (85, 76), (85, 68), (85, 59), (85, 50), (85, 41), (85, 33), (85, 24), (85, 15)],
        # --- 第 2 题 ---
        [(85, 15), (87, 19), (89, 24), (91, 28), (93, 33), (94, 37), (96, 41), (98, 46), (100, 50)],
        # --- 第 3 题 ---
        [(50, 100), (54, 98), (59, 96), (63, 94), (68, 93), (72, 91), (76, 89), (81, 87), (85, 85)],
        # --- 第 4 题 ---
        [(50, 100), (54, 89), (59, 79), (63, 68), (68, 58), (72, 47), (76, 36), (81, 26), (85, 15)],
        # --- 第 5 题 ---
        [(100, 50), (94, 56), (88, 63), (81, 69), (75, 75), (69, 81), (63, 88), (56, 94), (50, 100)],
        # --- 第 6 题 ---
        [(100, 50), (98, 54), (96, 59), (94, 63), (93, 68), (91, 72), (89, 76), (87, 81), (85, 85)],
        # --- 第 7 题 ---
        [(100, 50), (96, 56), (93, 63), (89, 69), (85, 75), (81, 81), (78, 88), (74, 94), (70, 100)],
        # --- 第 8 题 ---
        [(90, 100), (91, 99), (93, 98), (94, 96), (95, 95), (96, 94), (98, 93), (99, 91), (100, 90)],
        # --- 第 9 题 ---
        [(100, 70), (94, 74), (88, 78), (81, 81), (75, 85), (69, 89), (63, 93), (56, 96), (50, 100)],
        # --- 第 10 题 ---
        [(100, 70), (99, 74), (98, 78), (96, 81), (95, 85), (94, 89), (93, 93), (91, 96), (90, 100)],
        # --- 第 11 题 ---
        [(70, 100), (74, 96), (78, 93), (81, 89), (85, 85), (89, 81), (93, 78), (96, 74), (100, 70)],
        # --- 第 12 题 ---
        [(50, 100), (56, 99), (63, 98), (69, 96), (75, 95), (81, 94), (88, 93), (94, 91), (100, 90)],
        # --- 第 13 题 ---
        [(50, 100), (56, 94), (63, 88), (69, 81), (75, 75), (81, 69), (88, 63), (94, 56), (100, 50)],
        # --- 第 14 题 ---
        [(100, 90), (96, 91), (93, 93), (89, 94), (85, 95), (81, 96), (78, 98), (74, 99), (70, 100)],
        # --- 第 15 题 ---
        [(90, 100), (91, 94), (93, 88), (94, 81), (95, 75), (96, 69), (98, 63), (99, 56), (100, 50)],
    ]
    MANAGER_BASE_PAY = cu(10)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # 定义 15 个题目的选择字段 (值 1-9)
    svo_1 = models.IntegerField(label="第1题选择")
    svo_2 = models.IntegerField(label="第2题选择")
    svo_3 = models.IntegerField(label="第3题选择")
    svo_4 = models.IntegerField(label="第4题选择")
    svo_5 = models.IntegerField(label="第5题选择")
    svo_6 = models.IntegerField(label="第6题选择")
    svo_7 = models.IntegerField(label="第7题选择")
    svo_8 = models.IntegerField(label="第8题选择")
    svo_9 = models.IntegerField(label="第9题选择")
    svo_10 = models.IntegerField(label="第10题选择")
    svo_11 = models.IntegerField(label="第11题选择")
    svo_12 = models.IntegerField(label="第12题选择")
    svo_13 = models.IntegerField(label="第13题选择")
    svo_14 = models.IntegerField(label="第14题选择")
    svo_15 = models.IntegerField(label="第15题选择")

    # --- 结果存储字段 ---
    svo_selected_round = models.IntegerField(doc="系统随机抽中的回合 (1-15)")
    svo_earned_points = models.IntegerField(doc="抽中回合对应的点数")
    svo_payoff_money = models.CurrencyField(doc="最终转换成的金额")


# =============================================================================
# PAGES
# =============================================================================

class SVO_Introduction(Page):
    """SVO 任务说明"""

    @staticmethod
    def is_displayed(player):
        # 记得修改这里的 role 判断，根据实际情况 (Manager 或 Investor)
        # 如果是 Investor SVO：
        return player.participant.vars.get('role') == 'Manager'
        # 如果是 Manager SVO：
        # return player.participant.vars.get('role') == 'Manager'


class SVO_TaskPage(Page):
    """核心任务页面"""
    form_model = 'player'
    form_fields = [f'svo_{i}' for i in range(1, 16)]

    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('role') == 'Manager'  # 同上，需确认角色

    @staticmethod
    def vars_for_template(player):
        # 将数据传给前端进行渲染
        items = []
        for idx, row_data in enumerate(C.SVO_MATRICES):
            items.append({
                'id': idx + 1,
                'options': row_data
            })
        return {'items': items}

    @staticmethod
    def before_next_page(player, timeout_happened):
        # ==================================================
        # 核心收益计算逻辑
        # ==================================================

        # 1. 随机抽取一个回合 (1 到 15)
        selected_round = random.randint(1, 15)
        player.svo_selected_round = selected_round

        # 2. 获取玩家在该回合的选择 (1-9)
        # 使用 getattr 动态获取字段值，例如 'svo_3'
        field_name = f'svo_{selected_round}'
        choice_index = getattr(player, field_name)

        # 3. 查表获取 (Self, Other) 数据
        # C.SVO_MATRICES 是列表 (0-14)，choice_index 是选项 (1-9)
        # 修正索引：矩阵行索引 = selected_round - 1
        #           选项列索引 = choice_index - 1
        matrix_row = C.SVO_MATRICES[selected_round - 1]

        # 容错：如果玩家未选择(超时等情况)，默认选第一个，防止报错
        if choice_index is None:
            choice_index = 1

        outcome = matrix_row[choice_index - 1]

        self_points = outcome[0]  # 自己获得的点数
        other_points = outcome[1]  # 对方获得的点数 (如果需要给对方加钱，可在这里处理)

        # 4. 计算并累加收益
        player.svo_earned_points = self_points
        money = self_points * C.CONVERSION_FACTOR
        player.svo_payoff_money = money

        # 将金额累加到 oTree 的总 payoff 中
        player.payoff += money
        player.participant.vars['svopayoff'] = float(money)


class SyncFinal(WaitPage):
    wait_for_all_groups = True  # 全局等待
    title_text = "计算收益"
    body_text = "实验任务已全部完成，正在生成最终收益明细，等待其他玩家完成实验任务..."

    @staticmethod
    # 这里必须接收 subsession，因为 wait_for_all_groups = True
    def after_all_players_arrive(subsession):
        # 遍历所有小组进行计算
        for group in subsession.get_groups():
            p1 = group.get_player_by_id(1)
            p2 = group.get_player_by_id(2)

            if p1.participant.vars.get('role') == 'Manager':
                manager, investor = p1, p2
            else:
                manager, investor = p2, p1

            # 该阶段不再写入通用 investpayoff 键，避免与 y1/y2/y3 后缀收益混淆。
            # 仅保留诊断信息，便于回溯。
            manager.participant.vars['syncfinal_checked'] = True


page_sequence = [SVO_Introduction, SVO_TaskPage, SyncFinal]