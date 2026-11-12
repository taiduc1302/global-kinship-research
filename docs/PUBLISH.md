# Publish to GitHub (Windows PowerShell)

This is a one-time action. **Do not upload private case data.** The authoring connector could not create a GitHub repository or fork, so this starter was delivered as a complete local Git bundle and a separate source ZIP.

## Preferred: preserve Git history and pinned upstream

1. Open https://github.com/new in the account `taiduc1302`.
2. Set repository name `global-kinship-research`, choose **Public**, and leave **Add a README / .gitignore / license** unchecked so the repository stays empty. Create the repository.
3. Download `global-kinship-research-v0.1.bundle` to your local Downloads folder.
4. Open PowerShell and run:

```powershell
cd "$HOME\Downloads"
git clone ".\global-kinship-research-v0.1.bundle" "global-kinship-research"
cd ".\global-kinship-research"
git remote set-url origin "https://github.com/taiduc1302/global-kinship-research.git"
git push -u origin main
git submodule update --init --recursive
python -m unittest discover -s tests -v
```

If Git authentication fails, authenticate with GitHub using your normal credential manager. Do not paste any access tokens into chats, issues, or source files. The pinned upstream Git submodule is fetched from the original author at the exact reviewed commit.

## Source ZIP alternative

The `-source.zip` archive contains program source, examples, docs and skill, but **not Git history or upstream submodule contents**. You can inspect or develop the code by extracting it; for proper publication, the bundle method above is recommended. Never upload the ZIP as one compressed file and assume GitHub will unpack it.

## Optional separate fork of upstream

Visit https://github.com/DenisSergeevitch/ex-ussr-kinship-research and use GitHub's **Fork** action to create an independent `taiduc1302/ex-ussr-kinship-research`. This is distinct from the submodule; the main project currently points to the author's original repository. Preserve upstream LICENSE and notices. If you later change submodule origin to your fork, review its commit SHA rather than moving it to an unreviewed `main` tip.

## Local verification without GitHub Actions

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
kinship audit examples/synthetic-vietnam-korea-case.json
kinship plan korea --name "김하늘"
```

A structural test pass does not validate specific historical facts, archive access or correctness of family relationships.
