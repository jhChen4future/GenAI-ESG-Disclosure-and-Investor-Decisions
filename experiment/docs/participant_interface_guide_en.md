# Participant-interface guide — English edition

> **Important status note.** This document translates and explains the main participant-facing text in the oTree project. It is provided for international inspection only. It was not shown to participants, was not used during data collection, and is not a validated runnable English version of the experiment. The Simplified-Chinese templates and source code remain authoritative.

## 1. General participant instructions

The opening pages describe an academic decision experiment. Participants are asked to read all instructions carefully, make decisions independently, and avoid communicating with other participants during the session.

The main points conveyed by the interface are:

- A participant receives a CNY 5 participation fee.
- Additional earnings depend on decisions and task performance.
- Responses are recorded for research purposes and handled using participant codes rather than public names.
- The experiment contains multiple tasks, including a manager–investor decision task and a social allocation task.
- Some conditions may include content generated or analyzed by an AI system.
- Participants should not refresh pages, leave the experiment, or use outside assistance unless the experimenter instructs them to do so.
- Submitted decisions are generally final.

The code and the historical payment records should be consulted for the exact conversion between experimental points and cash in each task.

## 2. Task A: manager–investor experiment

Participants are assigned a role within a decision setting involving an ESG report. The two roles receive different information and have different incentives.

### 2.1 Manager role

The manager is responsible for an enterprise's ESG disclosure. In the implemented manager task, the manager privately learns that the enterprise's true ESG score is 50. The investor does not directly observe this value.

The manager chooses presentation characteristics for an ESG report. The key choices concern:

- **Textual complexity:** how easy or difficult the report's wording and sentence structure are to process.
- **Formatting or visual complexity:** how simple or elaborate the report's layout, tables, visual elements, and information organization are.

The interface explains that these presentation choices may affect how an investor interprets the enterprise's ESG performance. The manager is therefore making a strategic disclosure decision rather than changing the true ESG score.

The manager is shown five scenarios concerning the probability that an AI system will help the investor interpret the report. The exact scenario is part of the experimental information environment. After reviewing the scenario and available choices, the manager submits a final text-complexity and format-complexity decision. The page warns that the decision cannot be changed after submission.

The manager's task earnings depend positively on the investor's later rating:

\[
\text{manager payoff} = 10 + 0.5 \times \text{investor rating}.
\]

This payoff rule gives the manager an incentive to consider how the disclosure will influence the investor's judgment.

### 2.2 Investor role

The investor evaluates an enterprise on the basis of an ESG report. The investor does not observe the underlying task truth before making the estimate.

The investor workflow includes:

1. reading the role introduction and payoff rules;
2. completing scale-calibration pages;
3. reading the assigned ESG report;
4. viewing AI-generated assistance if assigned to the AI-assisted condition;
5. estimating the enterprise's true ESG score;
6. reporting confidence in the estimate;
7. answering report-comprehension questions;
8. reviewing the task result and earnings information where applicable.

### 2.3 Calibration pages

The investor interface uses reference examples at scores of 30, 60, and 90. These pages help participants understand what low, middle, and high values on the response scale represent. The reference values are instructional anchors, not participant responses.

### 2.4 Human-only and AI-assisted conditions

In the human-only condition, the investor reads and interprets the ESG report without an AI analysis being displayed.

In the AI-assisted condition, the experiment sends configured report information to an external chat-completions-style endpoint and displays the resulting analysis. The AI output is intended as decision support; the investor remains responsible for the final estimate and comprehension answers.

The English documentation does not reproduce a particular generated response because the treatment content may depend on the request and the configured model. A replication should record whether the request succeeded and preserve the exact content that participants actually saw.

### 2.5 Investor estimate and earnings

The true ESG score used to assess the investor's estimate is 60 in the implemented investor task. The accuracy component is:

\[
\text{estimate payoff} = \max(0, 55 - |\text{estimate} - 60|).
\]

An estimate closer to 60 therefore earns more points, subject to the floor at zero. The interface also asks the participant to report confidence in the estimate.

### 2.6 Comprehension quiz

After reading the report, the investor answers questions about its content. Each correct answer earns 6 points under the implemented rule. The quiz is designed to measure report understanding and to add an incentive for attentive reading.

When reconstructing results, the answer key and the exact number of items should be read from the relevant round's code. Stored quiz payoffs should be checked against recalculated scores.

## 3. ESG report materials

Some participant pages open local PDF files stored under `experiment/_static/*/reports_pdf/`.

These PDFs were created by the researcher as experimental stimuli. The author supplied authentic corporate ESG annual reports to an AI model and used prompts that imposed target requirements for textual complexity and formatting complexity. The AI-generated versions were then manually reviewed and fine-tuned by the author so that they more closely matched the intended experimental conditions.

The PDFs are therefore controlled research materials, not official company-issued ESG reports. They should not be described as statements published by the source companies. The construction process combines authentic-report inputs, AI-assisted generation under complexity constraints, and manual post-editing.

This guide does not translate the full PDF stimuli. The Chinese PDFs and the code paths that select them remain part of the historical experimental record.

## 4. Three report or industry rounds

The source tree contains `y1`, `y2`, and `y3` manager and investor apps. These represent separate industry/report versions within the broader design. The participant-facing sequence is structurally similar across the versions, while report content, stored field names, or round-specific details may differ.

An analyst should not merge the three versions solely by filename similarity. Build an explicit mapping from app, report PDF, industry, treatment, and round before estimating pooled effects.

## 5. Task B: Social Value Orientation

The SVO section asks participants to make 15 allocation decisions between themselves and another anonymous person. Each item presents possible divisions of points. Participants select the division they prefer.

The interface explains that:

- there is no single correct answer;
- choices should reflect the participant's own preference;
- one of the 15 decisions is randomly selected for payment;
- the participant's own points in the selected allocation determine their SVO earnings;
- the other person's allocation is also determined by the selected choice.

The implemented conversion for the participant's own selected points is:

\[
\text{SVO payoff} = 0.1 \times \text{own points}.
\]

Item-level choices should be retained even though only one item is selected for payment, because the full pattern is needed for any derived SVO measure.

## 6. Post-experiment questionnaire

The final questionnaire collects background and perception measures relevant to interpretation of the experiment. Depending on the exact model fields, these include demographic characteristics, academic or professional background, investment experience, familiarity with ESG, familiarity with generative AI, risk attitudes, and views about the decision process.

The questionnaire text should be interpreted through the Chinese templates and their coded response options. The English descriptions here summarize construct meaning; they do not create a new validated measurement instrument.

## 7. Payment display

The final pages present the participant's selected task earnings, SVO earnings, and fixed component according to the experimental code. The implemented final calculation includes a randomly selected incentivized main-task component, the SVO component, and a fixed 10-point amount. The general instructions separately describe the CNY 5 participation fee.

For historical payment reconciliation, use the actual exported primitives and the code in the payment app. Do not infer cash paid from a screenshot or summary label alone.

## 8. Key interface concepts translated

| Chinese interface concept | English rendering used in this guide |
|---|---|
| 生成式人工智能 | generative artificial intelligence |
| 环境、社会与治理（ESG） | environmental, social, and governance (ESG) |
| 企业真实ESG评分 | enterprise's true ESG score |
| 文本复杂度 | textual complexity |
| 格式复杂度 / 视觉复杂度 | formatting or visual complexity |
| 投资者判断 | investor judgment |
| 评分置信度 | confidence in the estimate |
| 理解测试 | comprehension quiz |
| 社会价值取向 | Social Value Orientation (SVO) |
| 实验报酬 | experimental earnings |

These renderings aim for conceptual consistency across the repository. They are not claims that the underlying Chinese scale items have undergone formal cross-language validation.

## 9. Translation coverage and exclusions

This guide covers the substantive meaning of the main instructions, manager and investor workflows, AI-assisted condition, payoff rules, comprehension task, SVO task, questionnaire, and payment display.

It intentionally does not:

- replace any Chinese template used in data collection;
- translate every button, validation message, or administrative label line by line;
- translate the full ESG-report PDFs;
- reproduce dynamic AI outputs;
- claim that an English-language participant version was piloted or validated;
- alter treatment logic or role incentives.

Researchers preparing an English replication should conduct forward translation, independent review or back-translation, pilot testing, measurement checks, and a new ethics and privacy review.

## 10. Research-use boundary

The available interface code documents a simple bachelor-thesis study, but the reported conclusions should not be used directly as established findings. The sample only met the study's minimum planned statistical-power requirement. The observed patterns are better viewed as exploratory, predictive, or correlational evidence.

Anyone interested in the question should replicate the study with an independently planned sample and transparent analysis protocol. For clarification about the original materials, contact the author through the associated academic homepage.