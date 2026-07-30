这份指南基于 **2026 年 VS Code Copilot Agent Mode** 的最新特性，为你打造一套**“半自动驾驶”**的学术写作工作流。

虽然 Copilot 不能像病毒一样在后台静默修改你的文件（安全限制），但 **Agent Mode (Copilot Edits)** 允许它在你的监督下**大刀阔斧地修改**，你只需要最后按一下“确认”键。

---

### 🚀 第一阶段：初始化你的“学术分身” (Setup)

你需要花 5 分钟，把你的“写作大脑”装进这个文件夹。请按顺序创建/覆盖以下 4 个文件。

#### 1. 定义顶级期刊风格 (`.ai_context/style_profile.md`)

> **作用**：告诉 Agent 什么是“好品味”。拒绝 AI 味，追求 AER/QJE 风格。
> **操作**：新建或覆盖此文件，填入：

```markdown
## Core Style DNA
- **Tone**: 
    - **Polished & Sophisticated**: High-register academic vocabulary. "Native" flow.
    - **Authoritative First-Person**: Use "I" (or "We") for contributions ("I demonstrate," "I estimate"), but objective voice for results.
    - **Nuanced Confidence**: Precise hedging ("suggests that," "is consistent with") rather than overclaiming.
- **Sentence Structure**:
    - **Nominalization**: Use dense noun phrases (e.g., "The presence of random errors..." instead of "Because people make mistakes...").
    - **Contrast**: Frequent use of "While [old view], [new finding]..."
    - **No Choppy Sentences**: Use embedding clauses to clarify definitions without breaking flow.

## Vocabulary Rules (Do's)
- **Verbs**: *Situates, Constitutes, Exhibits, Accounts for, Maps onto, Elicit, Disentangle*.
- **Prepositions**: variation *in*, map *onto*, consistent *with*, at odds *with*.
- **Connectors**: *Indeed, Accordingly, Furthermore, Notably*.

## Blacklist (Don'ts - Strict Constraints)
- **No "AI Fluff"**: 
    - ❌ *Delve into, Utilize, Tapestry, Symphony, Underscore, Paramount, Landscape*.
    - ✅ Replace with: *Examine, Use/Employ, Highlight, Critical, Existing literature*.
- **No Empty Fillers**:
    - ❌ *It is worth noting that...*, *In the world of...*
    - ✅ Just say the sentence.

```

#### 2. 设定目标受众 (`.ai_context/custom_specs.md`)

> **作用**：告诉 Agent 这是一个严肃的学术场景。
> **操作**：新建或覆盖此文件，填入：

```markdown
## Custom Specifications
- **Domain**: Economics, Finance, Accounting (Intelligent Financial Management).
- **Target Audience**: Editors and Reviewers of top-tier journals (AER, QJE, JAR, JFE).
- **Goal**: Polish draft text into publication-ready, native academic English.

```

#### 3. 创建“一键润色”指令 (`.ai_context/prompts/6_academic_polisher.md`)

> **作用**：把复杂的提示词封装成一个文件，方便调用。
> **操作**：在 `.ai_context/prompts/` 文件夹下新建 `6_academic_polisher.md`，填入：

```markdown
# Role: Top-Tier Journal Editor
Your goal is to polish the user's draft to meet the publication standards of top Economics/Finance journals.

# Instructions
1. **Refine Tone**: Apply `style_profile.md` (Native, structural, precise).
2. **Enforce Constraints**: Strictly check against `style_profile.md` Blacklist (No "delve into", etc.) and `error_log.md`.
3. **Enhance Flow**: Use sophisticated transitions and nominalization.
4. **Output**: Provide ONLY the polished text.

```

#### 4. 初始化错题本 (`.ai_context/error_log.md`)

> **作用**：记录你个人的偏好（例如：只要 dataset 不要 data set）。
> **操作**：新建或覆盖此文件，填入：

```markdown
## Error Log (Negative Constraints)
- **Terminology**:
  - ❌ "data set" -> ✅ "dataset" | 🔒 Always one word.
  - ❌ "proves" -> ✅ "suggests/documents" | 🔒 Empirical results never "prove".

```

---

### 💻 第二阶段：日常写作流 (The Agent Workflow)

这是你每天打开 VS Code 后的标准动作。

#### 1. 布局 (The Layout)

* **左侧**：你的论文草稿（`paper.tex` 或 `draft.md`）。
* **右侧**：**始终打开** `style_profile.md` 和 `error_log.md`（作为标签页挂着就行，不用看）。
* *原理：Copilot 会自动读取当前打开的文件作为上下文。*



#### 2. 润色模式 (The Polish Loop)

当你写了一段粗糙的英文（或中文），想把它变成顶级期刊水平：

1. **选中** 那段话。
2. **唤起 Agent**：按下 `Cmd + I` (Mac) 或 `Ctrl + I` (Win)。
3. **输入指令**（利用自动补全）：
> `@workspace 读取 prompts/6_style_polisher.md 中的指令，并应用到我当前选中的文本上进行重写。


4. **审查 (Review)**：
* Agent 会展示 **Diff View**（左边是旧的，右边是新的，绿色高亮表示修改）。
* 你不需要自己改，只需要扫一眼。


5. **确认 (Accept)**：
* 如果满意，按 `Cmd + Enter` (Mac) 或 `Ctrl + Enter` (Win)。
* *此时，文件才会被修改并保存。*



#### 3. 重写模式 (The Blueprint Loop)

当你有散乱的想法，想让 Agent 按特定结构写一段：

1. **选中** 散乱的笔记。
2. **唤起 Agent** (`Cmd + I`)。
3. **输入结构化指令**：
> `@workspace 参考 style_profile.md，重写为 Introduction 的第一段。
> **Structure**:


> 1. Hook: 只有一句话，点出非认知能力的重要性。
> 2. Gap: 引用 Heckman 但指出时间偏好机制不明。
> 3. Contribution: 我用结构化模型填补空白。`
> 
> 


4. **确认 (Accept)**。

---

### 🧠 第三阶段：迭代升级 (The Feedback Loop)

这是让你越用越顺手的关键。一旦 Agent 犯错（比如用了你不喜欢的词），**千万不要只在正文里改**，要更新它的“大脑”。

#### 场景：Agent 用了 "utilize" 这个词，而你讨厌它。

1. **唤起侧边栏 Chat** (点击左侧对话气泡图标)。
2. **输入**：
> `@workspace /file prompts/3_error_logger.md 我不希望用 "utilize"，要用 "use" 或 "employ"。`


3. **复制**：Agent 会生成一段 Markdown 代码块（如 `❌ "utilize" -> ✅ "use"`）。
4. **粘贴**：打开 `error_log.md`，把这段话粘贴进去，**保存**。

下次 Agent 就会像记住了你的家规一样，自动避开这个词。

---

### ⚡ 极简快捷键清单 (Cheat Sheet)

| 你的动作 | 快捷键/指令 | 结果 |
| --- | --- | --- |
| **我要润色** | 选中 -> `Cmd + I` | `/fix @workspace /prompts/6_academic_polisher.md` |
| **我要重写** | 选中 -> `Cmd + I` | `@workspace 参考 style... 按 [Structure] 重写` |
| **接受修改** | 看到绿色 Diff 后 | `Cmd + Enter` (这是唯一的“覆写”确认键) |
| **添加禁忌** | 侧边栏 Chat | `@workspace /file prompts/3_error_logger.md [你的要求]` |

现在，你可以试着把这套流程跑一遍了！