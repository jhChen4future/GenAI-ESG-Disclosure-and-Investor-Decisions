# Experiment code

This directory contains the oTree implementation of the bachelor-thesis experiment.

## Language and English documentation

The experiment was administered in Simplified Chinese. The Chinese participant-facing pages, questionnaires, and source comments are therefore the authoritative record of the implemented protocol.

For international inspection, this repository also provides:

- [English experiment audit and variable guide](./docs/experiment_audit_and_variable_guide_en.md)
- [English participant-interface guide](./docs/participant_interface_guide_en.md)

These English documents are translations and explanatory aids only. They were not shown to participants and do not constitute a separately validated English-language experiment.

## Local setup

1. Create and activate a Python environment.
2. Install the dependencies listed in `requirements.txt`.
3. Copy the repository-level `.env.example` to `.env` and provide your own values.
4. Start the project with the oTree command appropriate to your installed version.

The AI-assisted condition uses three provider-neutral environment variables:

```text
API_KEY=replace_with_your_own_key
API_ENDPOINT=https://your-provider.example/v1/chat/completions
API_MODEL=your-model-name
```

`API_ENDPOINT` must accept a chat-completions-style JSON request and bearer-token authentication. No service URL, provider-specific identifier, model name, or credential is embedded in the tracked code.

## ESG report stimuli

Some experiment pages read ESG-report PDFs from local folders under `experiment/_static/*/reports_pdf/`.

These PDFs are researcher-created experimental stimuli, not company-issued reports. They were produced by supplying authentic corporate ESG annual reports to an AI model together with prompts specifying target levels of textual complexity and formatting complexity. The generated materials were then manually reviewed and fine-tuned by the author so that they better matched the experimental conditions. This provenance should be preserved in any methodological description or replication.

The repository does not claim that the generated reports reproduce the source companies' statements, nor should the stimuli be represented as official corporate disclosures.

## Reproduction boundaries

The code archive supports inspection of the experimental workflow, variables, and treatment implementation. Complete numerical reproduction also requires the research data and analysis scripts. Those materials are not currently available in this repository because they have not yet been recovered from the original computer.

The reported thesis results should not be treated as established findings. The sample size only met the study's minimum planned statistical-power requirement, so the estimates are best understood as exploratory, predictive, or correlational evidence. Researchers interested in the question should run an independent replication rather than directly reuse the conclusions.

For urgent research enquiries, contact the author through the contact information on the associated academic homepage.

## Repository safety

The tracked project excludes local environment files, databases, participant exports, generated caches, and common oTree runtime artifacts. Before deployment, review the full configuration, replace all placeholders, and perform your own privacy and security checks.