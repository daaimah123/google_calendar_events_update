# Google Calendar Bulk Updater

A Python script to bulk update events in your Google Calendar based on various criteria.

## What This Does

This script allows you to:

- Find events by title, date range, or description
- Bulk update event properties (title, description, color, location)
- **Shift event dates** by days, weeks, or months
- **Adjust event times** while keeping the same date
- **Convert events to recurring** with custom patterns
- Filter events to only update future occurrences

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
3. If prompted, configure OAuth consent screen:
   - Choose "External" user type
   - Fill in app name and your email
   - Save and continue
4. Choose "Desktop app" as application type
5. Click "Create" and download the credentials
6. Rename the file to `credentials.json` and place it in the project root

**Important:** Add these Authorized Redirect URIs in your OAuth client settings:

- `http://localhost:8080/`
- `http://localhost`

### Step 3: Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz
```

### Step 4: First Run

On first run, the script will open a browser window for authentication. After authorizing, a `token.json` file will be created for future use.

## Usage Examples

See `example_usage.py` for common use cases:

### Basic Updates

- Update all events with a specific title
- Change event colors by keyword
- Bulk update event descriptions
- Add locations to events

### Date & Time Adjustments

- **Shift events** forward or backward by days/weeks/months
- **Adjust start/end times** for multiple events at once
- Filter to only update events after today

### Recurring Events

- Convert single events to recurring patterns
- Set recurrence by day of week (e.g., every Monday and Wednesday)
- Define end date or occurrence count

## Quick Start - Your Use Case

To update "Project Share & Weekly Survey" events from 8:00-8:50pm to 7:30-8:50pm:

```bash
python scripts/example_usage.py
```

The script runs `example_9_project_share_time_adjustment()` by default, which:

1. Finds all future "Project Share & Weekly Survey" events
2. Changes start time to 7:30 PM Pacific
3. Keeps end time at 8:50 PM Pacific
4. Runs in dry-run mode first (shows changes without applying)

To actually apply the changes, edit `example_usage.py` and set `dry_run=False`.

## Available Methods

### `find_events()`

Search for events by title, date range, or filter to events after a specific date.

### `bulk_update()`

Update title, description, location, or color for multiple events.

### `shift_event_dates()`

Move events forward or backward by days, weeks, or months.

### `adjust_event_times()`

Change start and/or end times while keeping the same date.

### `make_recurring()`

Convert events to recurring with custom frequency and patterns.

## Safety Features

- **Dry-run mode** by default - see changes before applying
- Detailed logging of all operations
- Error handling for individual events (one failure doesn't stop the batch)

## Troubleshooting

**Error 400: redirect_uri_mismatch**

- Add the redirect URIs listed in Step 2 to your OAuth client in Google Cloud Console

**No events found**

- Check your date range and title search terms
- Verify you're searching the correct calendar (default is 'primary')

**Authentication issues**

- Delete `token.json` and re-authenticate
- Ensure `credentials.json` is in the project root

## FAQ

**Does it handle multiple events at once?**
Yes, The scripts are specifically designed for bulk operations on multiple events:
      - `find_events()` returns a **list** of events (up to `max_results=100` by default)
      - All update methods (`bulk_update()`, `shift_event_dates()`, `adjust_event_times()`, `make_recurring()`) accept a **list of events** as the first parameter
      - They loop through all events in the list and apply changes to each one

```bash
# This finds MULTIPLE events
events = updater.find_events(
   title_contains="Project Share & Weekly Survey",
   start_date=datetime.utcnow(),
   end_date=datetime.utcnow() + timedelta(days=365)
)

# This updates ALL of them at once
updater.adjust_event_times(
   events,  # List of multiple events
   new_start_time="19:30",
   new_end_time="20:50",
   dry_run=True
)
```

**Are there required permissions?**
When logging into the OAuth scope `https://www.googleapis.com/auth/calendar`, you will have access to your pre-existing permissions for calendars where you have:
- **Owner** access - Full control
- **Make changes to events** - Can modify events