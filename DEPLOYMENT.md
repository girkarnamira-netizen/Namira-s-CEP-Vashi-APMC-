# Deployment Guide

## 1. Create the GitHub repository
1. Sign in to GitHub.
2. Click New repository.
3. Name the repository, choose Public or Private, and create it.
4. Do not initialize with a README if you plan to push an existing project.

## 2. Push the project
From the project folder run:

```bash
git init
git add .
git commit -m "Initial project commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 3. Connect to Streamlit Community Cloud
1. Open https://share.streamlit.io/
2. Sign in with GitHub.
3. Select the repository you just created.
4. Pick the branch and set the app file to `app.py`.

## 4. File to select
Use the repository root and select:
- App path: `app.py`
- Python version: default supported version

## 5. Deploy
Click Deploy. Streamlit Community Cloud will install dependencies from `requirements.txt` and start the app.

## 6. Update the app
After making changes locally:

```bash
git add .
git commit -m "Update dashboard"
git push origin main
```

The deployed app will update automatically after the push completes.

## 7. Important notes
- Keep all data files under the repository root or inside `data/`.
- Do not use local absolute paths.
- Ensure `app.py` is the entry point and `requirements.txt` includes all dependencies.
