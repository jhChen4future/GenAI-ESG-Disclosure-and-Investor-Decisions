# Experiment audit and variable guide — English edition

Status date: 2026-03-03  
Scope: oTree source under `experiment/`

> **Translation status.** This document is an English translation and technical interpretation aid. It was not shown to participants and was not used during data collection. The Simplified-Chinese source code, templates, and original Chinese guide remain the authoritative record of the implemented experiment.

## 1. Study structure

The project implements a repeated manager–investor experiment concerning ESG disclosure, report complexity, AI assistance, and investor judgment. Participants first read common instructions and then complete role-specific tasks. The main roles are:

- **Manager:** observes a private true ESG score and chooses how a report should be presented.
- **Investor:** reads the resulting ESG report, may receive AI assistance depending on treatment, estimates the true score, and completes comprehension and confidence measures.

The archive contains three industry/report rounds. It also contains a Social Value Orientation (SVO) task and a post-experiment questionnaire. Round-specific oTree apps retain separate fields so the collected exports can be reconstructed without assuming that every round used identical labels.

## 2. Technical audit

### 2.1 Blocking items reviewed

The audit checked whether the following components formed a coherent executable chain:

1. session configuration and app sequence;
2. role assignment and participant identifiers;
3. manager choices and treatment generation;
4. transfer of the selected report to the investor page;
5. treatment-specific AI requests;
6. investor estimates, quiz answers, and confidence reports;
7. task payoffs and final random payment selection;
8. SVO and questionnaire completion;
9. exportable tracking variables.

The implemented pages and models form that chain. The audit retained the original Chinese protocol and did not replace participant-facing text with an English-language intervention.

### 2.2 Logic clarifications incorporated in the archive

- Role-specific pages are controlled through oTree display conditions rather than by duplicating participant records.
- Investor treatment assignment is stored explicitly and should be used as the primary treatment indicator in analysis.
- Manager decisions generate report-complexity conditions before the investor reading stage.
- AI output is treated as treatment content and should not be reconstructed from memory or assumed to be identical across requests.
- Final earnings sample the relevant incentivized task according to the code rather than summing every hypothetical payoff.
- Page-entry, page-exit, and duration fields are tracking variables; they are not automatically clean behavioral measures and require screening.

### 2.3 Non-blocking improvements for future deployment

A new deployment should add or verify:

- a pinned Python and oTree environment;
- automated smoke tests for each treatment path;
- request timeouts, structured error handling, and a documented fallback for an unavailable AI endpoint;
- a preregistered exclusion and attrition policy;
- an explicit randomization check;
- browser and screen-size testing for report PDFs and charts;
- a stable, privacy-reviewed export procedure;
- a frozen copy or deterministic record of all treatment content sent to participants.

## 3. Experimental logic

### 3.1 Manager stage

The manager privately observes a true ESG score of 50 in the implemented task. The manager then selects disclosure characteristics, including textual complexity and visual or formatting complexity. The interface presents five probability scenarios describing how AI use may affect whether an investor correctly understands the report. The submitted choice is irreversible within the round.

The manager's task payoff is implemented as:

\[
\text{manager payoff} = 10 + 0.5 \times \text{investor rating}.
\]

This creates an incentive to influence the investor's reported assessment.

### 3.2 Investor stage

The investor reads the assigned report and estimates its underlying ESG score. Depending on treatment, the investor either interprets the report unaided or receives an AI-generated analysis. The code records the treatment, the estimate, confidence, quiz responses, timing, and relevant interaction traces.

The true ESG score used for the incentivized estimate is 60 in the investor task. Estimation payoff is:

\[
\text{estimate payoff} = \max(0, 55 - |\text{estimate} - 60|).
\]

The comprehension component awards 6 points for each correct answer. These rules should be verified against the relevant round file when rebuilding payment tables because task labels and stored fields can differ across apps.

### 3.3 Calibration prompts

Investor pages include reference values at 30, 60, and 90. These prompts help participants understand the response scale. Analysts should distinguish calibration-page exposure from the participant's final estimate and should not treat the reference values as observations.

### 3.4 SVO task

The SVO module contains 15 allocation decisions. One decision is selected for payment. The participant's own allocated points are converted at the implemented rate:

\[
\text{SVO payoff} = 0.1 \times \text{own points}.
\]

The original interface also describes the point-to-currency conversion used for the task. Researchers should follow the code and payment records if they need an exact historical reconciliation.

### 3.5 Final payment

The final payment page combines the randomly selected main-task payoff, the SVO payoff, and a fixed amount of 10 experimental currency units according to the implemented code. The general instructions also describe a participation fee of CNY 5. A reproduction should separate show-up compensation, experimental-currency calculations, and final cash conversion.

## 4. Variable dictionary

The names below describe the analytical meaning of the stored fields. Exact spellings should be taken from the oTree models and exports; fields are grouped by function so that round-specific variants can be harmonized deliberately.

### 4.1 Participant and session fields

| Field or field family | Meaning | Analysis note |
|---|---|---|
| `participant.code` | oTree participant identifier | Treat as an identifier, not a covariate. |
| `session.code` | Session identifier | Consider session clustering when appropriate. |
| `round_number` | oTree round index | Verify its mapping to industry/report version. |
| `role` / role indicator | Manager or investor assignment | Use to separate structurally different tasks. |
| treatment indicator | AI-assisted or human-only investor condition | Primary between-participant or round-level treatment field, depending on configuration. |
| industry/report identifier | Stimulus version or sector | Include in balance checks and fixed-effect specifications where justified. |

### 4.2 Manager variables

| Variable concept | Meaning | Suggested treatment |
|---|---|---|
| true ESG score | Private information shown to the manager | Design constant; do not model as observed variation if fixed. |
| text complexity choice | Selected level of linguistic or textual complexity | Main strategic-disclosure outcome. |
| format/visual complexity choice | Selected level of formatting complexity | Main strategic-disclosure outcome. |
| AI probability scenario | Manager belief or scenario regarding AI interpretation | Treat according to the randomized or elicited design role. |
| manager confirmation | Final submission of disclosure choices | Useful for completion checks. |
| manager page durations | Time on explanation and choice pages | Screen for implausible values before analysis. |
| linked investor rating | Investor's reported assessment associated with manager | Payoff input and possible strategic outcome. |
| manager payoff | Computed task earnings | Recompute from primitives for validation. |

### 4.3 Investor treatment and reading variables

| Variable concept | Meaning | Suggested treatment |
|---|---|---|
| AI-assistance indicator | Whether AI analysis was available | Primary treatment variable. |
| assigned report | Report/PDF shown in the round | Preserve version information. |
| report text complexity | Complexity condition embedded in the report | Treatment component or mediator depending on the estimand. |
| report format complexity | Formatting condition embedded in the report | Treatment component or mediator depending on the estimand. |
| AI request input | Treatment prompt/context sent to the endpoint | Sensitive methodological record; archive only after privacy and rights review. |
| AI response | Generated assistance shown to the investor | Treatment realization; do not assume uniformity. |
| reading-page duration | Time between entry and submission | Use after outlier and inactivity checks. |
| PDF or page interactions | Recorded reading behavior, where available | Define an aggregation rule before hypothesis testing. |

### 4.4 Investor outcome variables

| Variable concept | Meaning | Suggested treatment |
|---|---|---|
| ESG estimate | Investor's inferred true ESG score | Main judgment outcome. |
| absolute estimation error | Absolute difference from the task truth | Derive consistently from the coded truth value. |
| signed estimation error | Estimate minus task truth | Distinguishes overstatement from understatement. |
| confidence | Self-reported confidence in the estimate | Secondary outcome or mechanism measure. |
| comprehension responses | Answers to report-understanding questions | Score using the coded answer key. |
| comprehension score | Number of correct answers or points earned | Recompute and audit before use. |
| investor payoff | Incentive payment from accuracy and quiz rules | Validate from estimate and correct-answer fields. |

### 4.5 Tracking and quality-control fields

| Variable concept | Meaning | Suggested treatment |
|---|---|---|
| page entry timestamp | Time a page was entered | Used to reconstruct order and interruptions. |
| page exit timestamp | Time a page was submitted | Pair with entry time; check timezone and missingness. |
| elapsed seconds | Recorded duration | Winsorization or exclusion rules should be declared in advance. |
| completion flag | Whether the relevant page/task was completed | Use in attrition reporting. |
| error/fallback flag | Whether an external AI request failed or a fallback appeared | Essential for treatment-integrity checks. |
| refresh/revisit indicator | Repeated loading or return behavior | Review before interpreting durations. |

### 4.6 SVO variables

| Variable concept | Meaning | Suggested treatment |
|---|---|---|
| choice 1–15 | Allocation selected in each SVO item | Retain item-level responses. |
| own points | Points assigned to the participant | Payoff primitive. |
| other points | Points assigned to the paired person | Used to derive social-preference measures. |
| selected payment item | Randomly chosen incentivized item | Required for payment audit. |
| SVO payoff | Converted own points from selected item | Recompute from the selected item. |
| SVO angle/category | Derived social-preference index, if calculated | Document the exact scoring rule and missing-data handling. |

### 4.7 Questionnaire variables

The post-experiment questionnaire contains demographic and attitudinal measures. Likely field families include age, gender, education or academic background, investment experience, familiarity with ESG, familiarity with generative AI, risk preferences, and perceived usefulness or trust. The model files are the authoritative source for exact labels and response coding.

For reporting:

- present category counts and missingness;
- avoid attempting to identify individual participants from combinations of demographics;
- distinguish prespecified covariates from exploratory controls;
- do not recode ordinal answers as continuous without explanation.

## 5. Recommended derived variables

Create derived variables in a transparent analysis script rather than overwriting raw exports.

- `abs_error`: absolute distance between the investor estimate and the implemented true score.
- `signed_error`: investor estimate minus the implemented true score.
- `quiz_correct_count`: number of comprehension items answered correctly.
- `quiz_payoff_recalculated`: correct count multiplied by the coded per-item points.
- `estimate_payoff_recalculated`: payoff computed from the implemented accuracy formula.
- `total_reading_time`: prespecified sum of relevant report and AI-reading pages.
- `manager_complexity_index`: only if a documented rule justifies combining text and format choices.
- `ai_request_success`: whether the intended AI treatment was actually delivered.
- `round_or_stimulus_id`: a stable mapping from app/round to the ESG report used.

Every derived field should include its formula, source variables, missing-value rule, and valid range in the future analysis repository.

## 6. Analysis suggestions

### 6.1 Treatment effects

A primary analysis can compare AI-assisted and unaided investors on estimation error, signed judgment, comprehension, confidence, and reading time. Report raw group summaries before adjusted models. If assignment or repeated observations operate at a clustered level, standard errors and randomization inference should respect that structure.

### 6.2 Strategic disclosure

Manager text and format choices can be modeled as outcomes of the information environment or AI probability scenario. Because these outcomes may be ordinal, present the coding and test whether conclusions depend on linear versus categorical treatment.

### 6.3 Heterogeneity

Potential moderators include investment experience, ESG familiarity, generative-AI familiarity, risk preferences, and SVO. These analyses should be treated as exploratory unless prespecified. Avoid splitting a modest sample into many small subgroups.

### 6.4 Mechanisms

Possible mechanisms include comprehension, confidence, reading time, and the realized AI response. Mediation language should remain cautious: an observed association between treatment, a process measure, and an outcome does not by itself identify a causal mechanism.

### 6.5 Statistical interpretation

The thesis sample only met the minimum planned statistical-power requirement. The estimates should not be treated as established conclusions. Their appropriate role is exploratory, predictive, or correlational, and any substantive claim should be tested through an independent replication with a prospectively planned sample.

## 7. Data reshaping and validation

A future analysis pipeline should:

1. preserve the untouched oTree export;
2. build a participant-by-round long table;
3. create a documented mapping across the three manager and investor app versions;
4. verify role, treatment, report, and round consistency;
5. recompute quiz scores and payoffs from primitive fields;
6. identify incomplete sessions, duplicate identifiers, impossible values, and failed AI requests;
7. produce a de-identified analysis table;
8. generate all tables and figures from scripts rather than manual spreadsheet edits.

Validation tables should compare recorded and recomputed payoffs, show treatment counts by session and report version, summarize missingness, and list every exclusion with a reason.

## 8. Reviewer-friendly reporting checklist

A complete future report should state:

- the unit and method of randomization;
- the number assigned, started, completed, excluded, and analyzed;
- the exact treatment content and whether the AI response was dynamic;
- how AI request failures were handled;
- the origin and construction of ESG report stimuli;
- the payoff rules and exchange rate;
- the primary outcome and model specification;
- uncertainty intervals and effect sizes, not only thresholded significance;
- multiplicity and exploratory-analysis handling;
- the limited statistical power and need for replication.

## 9. ESG PDF provenance

Local PDFs under `experiment/_static/*/reports_pdf/` are researcher-created experimental stimuli. The author supplied authentic corporate ESG annual reports to an AI model and used prompts that specified desired levels of textual complexity and formatting complexity. The generated reports were then manually reviewed and fine-tuned to better satisfy the experimental conditions.

They are not official company-issued reports. A replication should either preserve these stimuli with the provenance statement or document a new, independently validated stimulus-construction process.

## 10. File map

- `experiment/settings.py`: oTree session and project configuration.
- `experiment/instruction/`: common experiment instructions.
- `experiment/manager_y1/`, `manager_y2/`, `manager_y3/`: manager tasks across report/industry rounds.
- `experiment/investor_y1/`, `investor_y2/`, `investor_y3/`: investor tasks and optional AI assistance.
- `experiment/SVO/`: Social Value Orientation task.
- `experiment/questionnaire/`: post-experiment questionnaire.
- `experiment/payment_info/`: payment summary and related pages.
- `experiment/_static/`: static assets, including local report PDFs.
- `experiment/docs/experiment_audit_and_variable_guide.md`: original Chinese audit and variable guide.
- `experiment/docs/participant_interface_guide_en.md`: English explanation of participant-facing content.

## 11. Use boundary

This archive makes the design inspectable, but the currently available files do not support full numerical reproduction because participant data and the final analysis scripts are not yet included. Do not directly reuse the thesis conclusions. Interested researchers should contact the author and independently replicate the study.