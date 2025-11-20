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
   GEMINI_API_KEY = "AIzaSyDCRUieEIlAaXiTTyB1b74dQYby52uxjr4"
   ```

6. **Save**
   - Click "Save" button
   - App will automatically restart with the new secret

## Verify It Works

- App will restart automatically
- Check app logs for any errors
- Upload soil PDF to test the functionality

## Security Notes

- Never commit `.env` file with API key to GitHub
- Streamlit Cloud secrets are encrypted
- Each app has isolated secrets
