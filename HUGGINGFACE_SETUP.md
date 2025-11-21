# Hugging Face Spaces Deployment Guide

## Step 1: Create Hugging Face Account
1. Go to https://huggingface.co
2. Sign up or log in
3. Go to https://huggingface.co/spaces

## Step 2: Create New Space
1. Click **"Create new Space"**
2. Fill in:
   - **Space name**: `SoilFinal` (or any name)
   - **License**: MIT
   - **Space SDK**: Select **Streamlit**
   - **Visibility**: Public
3. Click **"Create Space"**

## Step 3: Connect GitHub Repository
1. In your new Space, go to **Settings** (top right)
2. Scroll to **"Repository"** section
3. Click **"Clone repository"**
4. Paste: `https://github.com/shashankms2006/SoilFinal`
5. Click **"Clone"**

Hugging Face will automatically pull all files from your GitHub repo.

## Step 4: Add API Key Secret
1. Go to **Settings** → **Repository secrets**
2. Click **"Add a secret"**
3. Add:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: Your Gemini API key
4. Click **"Add secret"**

## Step 5: Deploy
1. Go back to **Files** tab
2. Hugging Face automatically detects `streamlit app.py` and deploys
3. Wait 2-3 minutes for build to complete
4. Your app will be live at: `https://huggingface.co/spaces/YOUR_USERNAME/SoilFinal`

## Troubleshooting

**App not starting?**
- Check **Logs** tab for errors
- Ensure `requirements.txt` has all dependencies
- Verify `GEMINI_API_KEY` secret is added

**API key not working?**
- Confirm secret name is exactly `GEMINI_API_KEY`
- Restart the Space: Settings → Restart Space

**PDF upload not working?**
- Ensure `pdfplumber` is in requirements.txt
- Check file size limits (Hugging Face allows up to 10GB)

## Your Space URL
Once deployed, share: `https://huggingface.co/spaces/YOUR_USERNAME/SoilFinal`
