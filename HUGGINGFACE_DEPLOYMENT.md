# Deploy on Hugging Face Spaces

## Step 1: Create Hugging Face Account
1. Go to https://huggingface.co
2. Click "Sign Up"
3. Create account with email/GitHub

## Step 2: Create New Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Space name**: `SoilFinal`
   - **License**: `MIT`
   - **Space SDK**: Select `Streamlit`
   - **Visibility**: `Public`
4. Click "Create Space"

## Step 3: Connect GitHub Repository
1. In your new Space, click "Files" tab
2. Click "Clone repository"
3. Paste: `https://github.com/shashankms2006/SoilFinal.git`
4. Wait for files to upload

## Step 4: Add API Key Secret
1. Click "Settings" (gear icon)
2. Scroll to "Repository secrets"
3. Click "Add secret"
4. Add:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyDCRUieEIlAaXiTTyB1b74dQYby52uxjr4`
5. Click "Add secret"

## Step 5: Deploy
1. Go back to "Files" tab
2. Space will auto-build and deploy
3. Wait 2-3 minutes for build to complete
4. Your app URL: `https://huggingface.co/spaces/YOUR_USERNAME/SoilFinal`

## Done! 🚀
Your app is now live on Hugging Face Spaces with full functionality!
