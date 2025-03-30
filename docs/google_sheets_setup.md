# Google Sheets API Setup Guide

## 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API for your project

## 2. Get API Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details
4. Click "Create and Continue"
5. Select role "Editor" (for read/write access)
6. Click "Done"
7. Click on the newly created service account
8. Go to "Keys" tab
9. Add Key > Create new key > JSON
10. Save the downloaded JSON file as `credentials.json`

## 3. Set Up Project Authentication
1. Create the config directory if it doesn't exist:
   ```bash
   mkdir -p config
   ```

2. Move your credentials file:
   ```bash
   mv path/to/downloaded/credentials.json config/credentials.json
   ```

3. Update your `.env` file with:
   ```bash
   GOOGLE_SHEETS_CREDENTIALS_FILE=config/credentials.json
   GOOGLE_SHEETS_TOKEN_FILE=config/token.json
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
   ```

4. Share your Google Sheet:
   - Open your Google Sheet
   - Click "Share"
   - Add the service account email (found in credentials.json) with Editor access

## 4. Get Your Spreadsheet ID
1. Open your Google Sheet
2. The ID is in the URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS-IS-YOUR-SPREADSHEET-ID]/edit
   ```
3. Copy this ID to your `.env` file

## 5. First-Time Authentication
The first time you run the application, it will:
1. Use the credentials.json to authenticate
2. Create a token.json file for future use
3. Store the token in config/token.json

## Security Notes
- Never commit credentials.json or token.json to version control
- Keep your .env file secure and never share it
- Regularly rotate your API keys for security
