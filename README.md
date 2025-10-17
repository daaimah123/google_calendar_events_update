# Google Calendar Bulk Updater
A Python script to bulk update events in your Google Calendar based on various criteria.

## Purpose
- Find events by title, date range, or description
- Bulk update event properties (title, description, color, location)
- Move events to different times
- Add or remove attendees in bulk

## Prerequisites
1. **Python 3.7+** installed on your system
2. **Google Cloud Project** with Calendar API enabled
3. **OAuth 2.0 credentials** from Google Cloud Console

## Setup Instructions

### Step 1: Enable Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### Step 2: Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as application type
4. Download the credentials JSON file
5. Rename it to `credentials.json` and place it in the same directory as the script

### Step 3: Install Dependencies
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 4: First Run
On first run, the script will open a browser window for authentication. After authorizing, a `token.json` file will be created for future use.

**Authentication Setup**
- Create Google Cloud project and enable Calendar API
- Download OAuth credentials
- First run authenticates and saves token for future use

**Finding Events**
- Search by title, date range, or get all events
- Returns list of matching events

**Bulk Updates**
- Modify title, description, location, or color
- Dry run mode shows changes before applying
- Processes all matching events

**Execution**
- Run with `python scripts/calendar_updater.py` for basic test
- Use `example_usage.py` for common scenarios
- Customize for your specific needs

## Usage Examples
See `example_usage.py` for common use cases:
- Update all events with a specific title
- Change event colors by keyword
- Bulk update event descriptions
- Move events to different times
