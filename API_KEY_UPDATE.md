# API Key Compromised - Update Required

Your Gemini API key has been reported as leaked and is no longer valid.

## Steps to Fix

1. **Generate New API Key**
   - Go to: https://ai.google.dev/
   - Click "Get API Key"
   - Create a new API key in Google Cloud Console
   - Copy the new key

2. **Update Streamlit Cloud Secrets**
   - Go to: https://share.streamlit.io
   - Click your `SoilFinal` app
   - Click ⋮ → Settings → Secrets
   - Replace old key with new one:
   ```
   GEMINI_API_KEY = "your_new_api_key_here"
   ```
   - Click Save

3. **Reboot App**
   - Click ⋮ → Reboot app
   - App will restart with new key

## Local Development

Update `.env` file:
```
GEMINI_API_KEY = "your_new_api_key_here"
```

## Security Notes

- Never commit `.env` with API keys to GitHub
- Use `.env.example` as template
- Regenerate keys if compromised
