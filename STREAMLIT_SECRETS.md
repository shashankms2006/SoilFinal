# Adding GEMINI_API_KEY to Streamlit Cloud

## Steps to Add Secret

1. **Go to Streamlit Cloud Dashboard**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub

2. **Select Your App**
   - Click on `SoilFinal` app

3. **Access App Settings**
   - Click the three dots (⋮) menu in top right
   - Select "Settings"

4. **Go to Secrets Section**
   - Click "Secrets" tab on the left sidebar

5. **Add GEMINI_API_KEY**
   - In the text area, paste:
   ```
   GEMINI_API_KEY = "your_actual_gemini_api_key_here"
   ```
   - Replace `your_actual_gemini_api_key_here` with your actual API key

6. **Save**
   - Click "Save" button
   - App will automatically restart with the new secret

## Getting Your GEMINI_API_KEY

1. Go to: https://ai.google.dev/
2. Click "Get API Key"
3. Create new API key in Google Cloud Console
4. Copy the key and paste in Streamlit Cloud secrets

## Verify It Works

- App will restart automatically
- Check app logs for any errors
- Upload soil PDF to test the functionality

## Security Notes

- Never commit `.env` file with API key to GitHub
- Streamlit Cloud secrets are encrypted
- Each app has isolated secrets
