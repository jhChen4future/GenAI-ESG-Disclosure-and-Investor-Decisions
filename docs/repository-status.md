# Repository status

Last organized: July 30, 2026.

## Available

- final Chinese bachelor's thesis with an English filename;
- sanitized oTree 5.11.1 experiment source;
- participant-facing templates and static report materials;
- Chinese experiment audit and variable guide;
- English project overview, citation metadata, and reproducibility notes.

## Not yet available

- data-cleaning and statistical-analysis scripts;
- figure-generation scripts;
- participant-level research data;
- a pinned, containerized reconstruction of the historical AI service.

The analysis scripts are stored on another laptop that is not currently in use. They can be added later after a privacy and secret scan. See [`analysis/README.md`](../analysis/README.md) for the public-facing note.

## Safety actions completed

- excluded databases, environment folders, caches, IDE metadata, and backups;
- removed an embedded API credential from all three investor apps;
- converted API, admin-password, and oTree-secret configuration to environment variables;
- retained only example room labels.

## Suggested next update

When the other laptop is available, add the analysis scripts on a dedicated branch, document software versions and input/output paths, run a secret scan, and compare every reproduced table against the thesis before merging.
