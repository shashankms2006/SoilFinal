# Streamlit Cloud Deployment

## Step 1: Prepare Your Repository
Ensure your GitHub repo has:
- `streamlit app.py` (main file)
- `requirements.txt` (all dependencies)
- All supporting Python files

## Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Select:
   - **Repository**: shashankms2006/SoilFinal
   - **Branch**: main
   - **Main file path**: streamlit app.py
4. Click **"Deploy"**

## Step 3: Add Secrets
1. Go to app settings (gear icon)
2. Click **"Secrets"**
3. Add:
   ```
   GEMINI_API_KEY = your_api_key_here
   ```
4. Save

## Step 4: Access Your App
Your app will be live at: `https://share.streamlit.io/shashankms2006/SoilFinal/main/streamlit%20app.py`

Done! Your app is deployed.
