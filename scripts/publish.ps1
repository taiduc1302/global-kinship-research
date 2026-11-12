# Run ONLY after creating empty taiduc1302/global-kinship-research on GitHub.
# Requires a normal Git installation and credentials configured locally.
param([string]$Remote = 'https://github.com/taiduc1302/global-kinship-research.git')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.git')) { throw 'Use the Git bundle/clone instructions, not the source ZIP, to retain the pinned submodule commit.' }
git remote remove origin 2>$null
git remote add origin $Remote
git push -u origin main
if ($LASTEXITCODE -ne 0) { throw 'Git push failed; verify repository ownership and authentication.' }
git submodule update --init --recursive
