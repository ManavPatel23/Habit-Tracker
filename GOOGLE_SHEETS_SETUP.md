# Google Sheets API Setup Guide

This guide will help you set up automatic Google Sheets synchronization for your Habit Tracker app.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Habit Tracker")
4. Click "Create"

## Step 2: Enable Google Sheets API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Also enable "Google Drive API" (search and enable it)

## Step 3: Create a Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Enter a name (e.g., "habit-tracker-service")
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 4: Generate Service Account Key

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" → "Create new key"
5. Choose "JSON" format
6. Click "Create"
7. The JSON file will download automatically

## Step 5: Configure the App

1. Rename the downloaded JSON file to `google_credentials.json`
2. Place it in the same folder as your `app.py` file
3. **Important**: Never commit this file to version control!

## Step 6: Share Your Google Sheet

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1jiMRMTmGRgk_i4vLLDdIUR8y4f95g1aVmvMgy0yzpMw/edit
2. Click "Share" (top right)
3. Add the service account email (found in your `google_credentials.json` file under `client_email`)
4. Give it "Editor" permissions
5. Click "Send"

## Step 7: Install Dependencies

Run this command in your terminal:

```bash
pip install -r requirements.txt
```

## Step 8: Test the Setup

1. Run your Streamlit app: `streamlit run app.py`
2. In the sidebar, expand "☁️ Google Sheets Sync"
3. You should see "🔑 Google Sheets API credentials found - Auto-sync enabled!"
4. Try adding a habit activity - it should automatically save to Google Sheets

## Troubleshooting

### "Error initializing Google Sheets client"
- Make sure `google_credentials.json` is in the correct location
- Check that the JSON file is valid
- Verify the service account has the correct permissions

### "Error saving to Google Sheets"
- Make sure you shared the Google Sheet with the service account email
- Check that the service account has "Editor" permissions
- Verify the Google Sheets API is enabled in your project

### "Permission denied"
- Double-check that the service account email is added to the Google Sheet
- Make sure the service account has "Editor" access, not just "Viewer"

## Security Notes

- Never share your `google_credentials.json` file
- Add `google_credentials.json` to your `.gitignore` file
- The service account only has access to the specific Google Sheet you shared

## What This Enables

Once set up, your Habit Tracker will:
- ✅ Automatically save data to Google Sheets when you add/remove activities
- ✅ Automatically load data from Google Sheets when you refresh
- ✅ No more manual copying and pasting of JSON data
- ✅ Seamless synchronization across devices

Enjoy your fully automated habit tracking! 🎉
