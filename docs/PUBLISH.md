# Repository publication and local startup

Canonical source repository: https://github.com/taiduc1302/global-kinship-research

v0.1 was published directly via the connected GitHub integration. The source repository has the original ex-USSR project linked as a Git **submodule** at a pinned upstream commit and preserves its separate license. GitHub ZIP downloads do **not** include submodule contents; the optional `import-ex-ussr` command imports files obtained separately from the original project.

For v0.2, contributors can download the source ZIP in the GitHub browser and, on Windows with Python 3.10+, double-click `scripts/Launch-Global-Kinship.cmd` to run the local workbench. This does not require PowerShell, GitHub Actions or hosting personal family data online.

Before publishing any release:

1. Run `PYTHONPATH=src python -m unittest discover -s tests -v` locally.
2. Check the source for real family data, secrets and restricted documents.
3. Check changed external dependencies and license/notice obligations.
4. For frontend changes, run a browser test at desktop and mobile sizes.
5. Record what was actually tested. Do not claim live archive or model integration if only mocks were used.
6. Verify the GitHub commit SHA, README, package data and `upstreams` submodule pin after the push.

No public website should host real cases until a separate privacy, authentication and storage design is approved.
