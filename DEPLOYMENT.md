# Streamlit Cloud Deployment Guide

## Step 1: Push to GitHub

```bash
cd "d:\Desktop\Mini Project\Codes\SoilFinal"
git init
git add .
git commit -m "Initial commit: Smart AI Agriculture app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/SoilFinal.git
git push -u origin main
```

## Step 2: Go to Streamlit Cloud

1. Visit https://share.streamlit.io
2. Sign in with GitHub account (create if needed)

## Step 3: Connect Repository

1. Click "New app"
2. Select:
   - Repository: `YOUR_USERNAME/SoilFinal`
   - Branch: `main`
   - Main file path: `streamlit app.py`
3. Click "Deploy"

## Step 4: Add GEMINI_API_KEY Secret

1. In Streamlit Cloud dashboard, go to app settings
2. Click "Secrets"
3. Add:
   ```
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
4. Save

## Step 5: App Deploys Automatically

- Streamlit Cloud will automatically deploy
- App URL: `https://share.streamlit.io/YOUR_USERNAME/SoilFinal`
- Any push to GitHub main branch auto-redeploys

## Environment Variables

The app reads from:
- `.env` file (local development)
- Streamlit Cloud Secrets (production)

Both use `GEMINI_API_KEY` variable.

## Troubleshooting

- **Import errors**: Check requirements.txt has all dependencies
- **API key issues**: Verify GEMINI_API_KEY in Streamlit Cloud secrets
- **File not found**: Ensure all Python files are in repository root
- **CSS not loading**: Check smart_style.css is in same directory as streamlit app.py
