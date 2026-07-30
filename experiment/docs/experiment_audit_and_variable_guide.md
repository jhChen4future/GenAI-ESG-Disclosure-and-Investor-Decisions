# ESG-AI 实验程序技术审计与变量使用手册

> 版本日期：2026-03-03  
> 审计范围：`instruction`、`manager_y1/y2/y3`、`investor_y1/y2/y3`、`svo_investor`、`svo_manager`、`questionnaire`、`settings.py`

---

## 1) 技术审计结论（客观）

### 1.1 自动化检查
- 已执行全项目错误检查：**未发现语法/模板静态错误**。

### 1.2 关键逻辑链检查
- 角色与处理分配：在 `manager_y1` 中完成（Manager/Investor + AI/Human）。
- 三轮主任务：`manager_y1→investor_y1`，`manager_y2→investor_y2`，`manager_y3→investor_y3`。
- SVO：Investor 与 Manager 各自完成 15 题并记录 `svopayoff`。
- 最终结算：`questionnaire` 随机抽取 `y1/y2/y3` 的任务收益 + `svopayoff` + 出场费。

### 1.3 本次已修复的问题
1. **角色判断一致性问题（代码级）**  
   - 三轮 `investor` 的 `Introduction.is_displayed` 从 `player.participant.role` 统一修复为 `player.participant.vars.get('role')`。
2. **说明文本与代码口径不一致（文档级）**  
   - Investor 收益公式文本已与代码一致：`max(0, 55-|估值-真实值|)+quiz奖励`。
   - Manager 可控维度文本已与代码一致：当前仅两维可选，信息显著性固定。
   - 全局说明中“任务随机排序”改为“按系统设定顺序”。
   - SVO 说明中“最终点数=自己+对方”改为“按自己点数结算”（与代码一致）。

### 1.4 仍建议优化（非阻塞）
- `questionnaire/__init__.py` 仍保留较多 `print` 调试日志；正式实验建议降噪或改为受控日志开关。
- `settings.py` 中 `PARTICIPANT_FIELDS` 仍是旧字段集合（当前主要使用 `participant.vars`，不影响运行，但可清理以减少误解）。
- 若投稿要求“预注册可复现”，建议补充一份参数冻结说明（`MAX_ACCURACY_PAYOFF`、`QUIZ_BONUS`、`CONVERSION_FACTOR`、抽样规则）。

---

## 2) 收益逻辑总览

## 2.1 任务A（ESG 管理者-投资者博弈，三轮）

### 投资者（每轮 y）
- 真实值：`TRUE_COMPANY_VALUE = 60`
- 估值误差：`diff_y = |estimated_score_y - 60|`
- 准确性收益：`acc_pay_y = max(0, 55 - diff_y)`
- 理解题收益：`quiz_pay_y = 6 × correct_count_y`（每轮3题）
- 投资者任务收益：

\[
\text{investpayoff}_y = acc\_pay_y + quiz\_pay_y
\]

### 管理者（每轮 y）
- 管理者任务收益（由投资者给分决定）：

\[
\text{mgrpayoff}_y = 10 + 0.5 \times \text{investor\_rating}_y
\]

其中 `investor_rating_y = estimated_score_y`。

## 2.2 任务B（SVO）
- 15题中随机抽1题。
- 取被抽中题目中“自己点数”`self_points`。
- 货币转换：

\[
\text{svopayoff} = self\_points \times 0.1
\]

## 2.3 最终支付（questionnaire）
- 从 `y1/y2/y3` 中随机抽取一轮任务A收益：`selected_round_task_payoff`
- 最终总收益：

\[
\text{total\_final\_payoff} = \text{selected\_round\_task\_payoff} + \text{svopayoff} + 10
\]

---

## 3) 变量字典（核心分析版）

> 说明：下面按“推荐分析优先级”列出。字段已覆盖主效应、异质性、机制与行为过程分析。

## 3.1 实验分组与基础键（`participant.vars`）

| 变量名 | 类型 | 含义 | 生成位置 | 典型用途 |
|---|---|---|---|---|
| `role` | str | 角色（Manager/Investor） | `manager_y1` 分组阶段 | 分组回归、样本筛选 |
| `treatment` | str | 环境处理（AI/Human） | `manager_y1` 分组阶段 | 主效应变量 |
| `manager_y1_done/y2_done/y3_done` | bool | 管理者是否完成该轮策略 | `manager_y*` | 等待页状态控制 |
| `selected_round_name` | str | 最终抽中的任务A轮次（y1/y2/y3） | `questionnaire` | 结算追踪 |
| `svopayoff` | float | SVO收益 | `svo_investor` 或 `svo_manager` | 最终支付、控制变量 |

## 3.2 Manager 决策变量（数据库字段，三轮同构）

| 变量名 | 类型 | 含义 | 用途 |
|---|---|---|---|
| `strat_0_l`, `strat_0_f` | int | 假设对手 0% AI 时策略（语言、格式） | 策略函数估计 |
| `strat_50_l`, `strat_50_f` | int | 假设对手 50% AI 时策略 | 风险中间态响应 |
| `strat_100_l`, `strat_100_f` | int | 假设对手 100% AI 时策略 | AI对手适配 |
| `applied_scenario` | str | 实际生效场景（按 treatment） | 执行一致性检查 |
| `strategy_form_seconds` | float | 策略形成时长（秒） | 机制：深思熟虑/复杂策略 |

### Manager 跨轮 participant 键
| 变量名 | 含义 |
|---|---|
| `final_report_text(_y2/_y3)` | 对投资者展示的最终报告文本 |
| `final_linguistic(_y2/_y3)` | 最终语言复杂度 |
| `final_format(_y2/_y3)` | 最终格式复杂度 |
| `final_proximity(_y2/_y3)` | 最终显著性（当前固定） |
| `manager_strategy_form_seconds_y1/y2/y3` | 每轮策略形成时间 |
| `mgr_score_y1/y2/y3` | 实际收到投资者打分 |
| `mgr_base_y1/y2/y3` | 基础收益部分 |
| `mgr_bonus_y1/y2/y3` | 评分奖金部分 |
| `investpayoff_y1/y2/y3` | 管理者在该轮任务A收益 |

## 3.3 Investor 决策与行为变量（数据库字段，三轮同构）

| 变量名 | 类型 | 含义 | 用途 |
|---|---|---|---|
| `estimated_score` | int | 对公司真实分值估计(0-100) | 主要行为结果 |
| `illusion_confidence` | int | 决策置信度(0-100) | 能力错觉/校准分析 |
| `quiz_1`,`quiz_2`,`quiz_3` | str/int/float | 理解测试作答 | 操作有效性、学习程度 |
| `payoff_from_accuracy` | currency | 准确性收益（页面内） | 收益分解 |
| `payoff_from_quiz` | currency | 理解题收益（页面内） | 收益分解 |
| `chat_history` | longtext | AI对话历史 | 文本机制（可选NLP） |
| `seen_report_text` | longtext | 读到的报告文本 | 可追溯性 |

### Investor 新增行为埋点字段
| 变量名 | 类型 | 含义 | 用途 |
|---|---|---|---|
| `raw_text_access_count` | int | 原始PDF查看动作累计（兼容旧日志） | 阅读深度代理 |
| `raw_pdf_open_count` | int | 打开“原始PDF”次数 | 信息搜寻行为 |
| `calibration_open_count` | int | 打开校准弹窗次数 | 规则依赖程度 |
| `report_new_window_click_count` | int | 新窗口打开报告次数 | 外部阅读偏好 |
| `quick_prompt_click_count` | int | 快捷提示按钮点击次数 | prompt工程倾向 |
| `manual_prompt_send_count` | int | 手动输入发送次数 | 主动探索强度 |
| `quick_prompt_send_count` | int | 快捷按钮发送次数 | 模板依赖程度 |
| `chat_send_count` | int | 总发送次数 | AI交互强度 |

### Investor 跨轮 participant 键
| 变量名 | 含义 |
|---|---|
| `investpayoff_y1/y2/y3` | 该轮投资者任务收益 |
| `inv_accuracy_pay_y1/y2/y3` | 该轮准确性收益 |
| `inv_quiz_pay_y1/y2/y3` | 该轮理解题收益 |
| `inv_true_val_y1/y2/y3` | 该轮真实值（当前固定60） |
| `inv_est_val_y1/y2/y3` | 该轮估值 |
| `inv_report_open_count_y1/y2/y3` | 该轮报告打开次数 |
| `inv_calibration_open_count_y1/y2/y3` | 该轮校准弹窗打开次数 |
| `inv_report_new_window_click_count_y1/y2/y3` | 该轮新窗口查看次数 |
| `inv_quick_prompt_click_count_y1/y2/y3` | 该轮快捷提示点击次数 |
| `inv_manual_prompt_send_count_y1/y2/y3` | 该轮手动发送次数 |
| `inv_quick_prompt_send_count_y1/y2/y3` | 该轮快捷发送次数 |
| `inv_chat_send_count_y1/y2/y3` | 该轮总聊天发送次数 |

## 3.4 SVO 变量（Investor/Manager 同构）

| 变量名 | 类型 | 含义 | 用途 |
|---|---|---|---|
| `svo_1`~`svo_15` | int | 15题各自选项(1-9) | 社会偏好异质性 |
| `svo_selected_round` | int | 随机抽中的题号 | 可复核性 |
| `svo_earned_points` | int | 被抽中题自己的点数 | 支付原始变量 |
| `svo_payoff_money` | currency | SVO货币收益 | 支付分解 |

## 3.5 Questionnaire 终局变量

### 人口学与背景
`age`, `gender`, `major`, `grade`, `GPT`, `major_background`, `investment_exp`, `risk_preference`

### 机制量表（19题，Likert 1-7）
- A 认知负荷：`cognitive_effort`, `information_overload`
- B 操纵感知：`perceived_manipulation`, `framing_bias`
- C AI信任依赖：`ai_trust`, `ai_reliance`, `ai_dependence`
- D 错觉与校准：`ai_illusion`, `ai_mislead`, `confidence_calibration`
- E 归因与质量：`attribution_error`, `decision_accountability`, `perceived_decision_quality`
- F Prompt工程：`prompt_engineering_use`, `prompt_iteration`, `prompt_specificity`
- G 面向AI策略：`ai_counterstrategy_intent`, `ai_detectability_belief`, `human_ai_differentiation`

### 支付落库
`payoff_task_y1`, `payoff_task_y2`, `payoff_task_y3`, `payoff_svo`, `selected_round`, `selected_round_task_payoff`, `payoff_from_experiment`, `total_final_payoff`, `suggestion`

---

## 4) 如何用这些变量做实证（主结果/异质性/机制）

## 4.1 主结果检验（Treatment Effect）

### 投资者主结果
- 因变量建议：
  - `abs_error_y = |inv_est_val_y - 60|`（越小越好）
  - `investpayoff_y`
  - `illusion_confidence`
- 核心自变量：`treatment`（AI=1, Human=0）
- 基准模型：

\[
Y_{iy} = \alpha + \beta \cdot AI_i + \gamma X_i + \delta_y + \varepsilon_{iy}
\]

`X_i` 包括 `risk_preference`, `investment_exp`, `major_background`, `GPT` 等。

### 管理者主结果
- 因变量建议：
  - `strat_100_l - strat_0_l`、`strat_100_f - strat_0_f`（对AI适配强度）
  - `strategy_form_seconds`
  - `investpayoff_y`（管理者收益）
- 检验：处理组下策略是否更“对AI定制”。

## 4.2 异质性分析（Heterogeneity）

### 预设分层
- 高/低AI使用频率（`GPT`）
- 商科背景（`major_background`）
- 投资经验（`investment_exp`）
- 风险偏好（`risk_preference`）

### 交互模型
\[
Y_{iy} = \alpha + \beta_1 AI_i + \beta_2 H_i + \beta_3 (AI_i \times H_i) + \gamma X_i + \delta_y + \varepsilon_{iy}
\]
其中 `H_i` 是异质性维度。

## 4.3 机制分析（Mechanism）

### 机制1：AI交互行为路径
- 中介候选：
  - `inv_chat_send_count_y`
  - `inv_manual_prompt_send_count_y`
  - `inv_quick_prompt_send_count_y`
  - `inv_calibration_open_count_y`
- 目标：检验 AI 处理是否通过“信息搜寻强度/提示词工程”影响估值误差与收益。

### 机制2：主观量表路径
- 中介候选：`ai_trust`, `ai_reliance`, `ai_dependence`, `prompt_engineering_use`, `information_overload`。
- 方式：中介回归或 SEM（如有样本量支持）。

### 机制3：管理者策略形成路径
- 中介候选：`strategy_form_seconds`, `human_ai_differentiation`, `ai_counterstrategy_intent`。
- 目标：解释“为何管理者会针对AI对手选择不同参数组合”。

---

## 5) 数据整理建议（可直接执行）

1. 构建长表（participant × round）
- `round ∈ {y1,y2,y3}`
- 将 `inv_*_y1/y2/y3`、`mgr_*_y1/y2/y3` reshape 为长格式。

2. 构造关键派生变量
- `abs_error = abs(inv_est_val - 60)`
- `prompt_share = inv_quick_prompt_send_count / inv_chat_send_count`
- `deliberation_log = log(1 + strategy_form_seconds)`

3. 处理极值与缺失
- 对时长和计数变量做 winsorize（1%/99%）
- 明确区分结构性缺失（非该角色）与随机缺失。

---

## 6) 审稿友好型说明（建议写入论文附录）

- 报酬函数、随机抽样规则、参数值（55/6/0.1/10）需在附录逐条列明。
- 说明 AI 助手使用的是预设 API 接口和固定 system prompt 框架。
- 报告参数空间实际为二维可选（L/F），第三维在本版固定。
- 行为日志变量（按钮点击、聊天发送、策略形成时长）用于机制识别与稳健性检验。

---

## 7) 本手册对应文件（便于复核）

- `settings.py`
- `instruction/Instruction.html`
- `manager_y1/__init__.py`, `manager_y2/__init__.py`, `manager_y3/__init__.py`
- `manager_y1/Introduction.html`, `manager_y2/Introduction.html`, `manager_y3/Introduction.html`
- `investor_y1/__init__.py`, `investor_y2/__init__.py`, `investor_y3/__init__.py`
- `investor_y1/Introduction.html`, `investor_y2/Introduction.html`, `investor_y3/Introduction.html`
- `investor_y1/InvestorReading.html`, `investor_y2/InvestorReading.html`, `investor_y3/InvestorReading.html`
- `svo_investor/__init__.py`, `svo_manager/__init__.py`
- `svo_investor/SVO_Introduction.html`, `svo_manager/SVO_Introduction.html`
- `questionnaire/__init__.py`, `questionnaire/MechanismSurvey.html`, `questionnaire/End.html`
