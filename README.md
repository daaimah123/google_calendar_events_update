# Google Calendar Bulk Updater

A Python script to bulk update events in your Google Calendar based on various criteria.

## Purpose
- Find events by title, date range, or description
- Bulk update event properties (title, description, color, location)
- Shift event dates by days, weeks, or months
- Adjust event times while keeping the same date
- Convert events to recurring with custom patterns
- Filter events to only update future occurrences

## Prerequisites
1. Python 3.7+ installed on your system
2. Google Cloud Project with Calendar API enabled
3. OAuth 2.0 credentials from Google Cloud Console

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
- Shift events forward or backward by days/weeks/months
- Adjust start/end times for multiple events at once
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
- Dry-run mode by default - see changes before applying
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
- Owner access - Full control
- Make changes to events - Can modify events

**What are the usecases for this program?**
#### Event Discovery & Filtering
1. List all calendars you have access to with their IDs and permissions
2. Find all events within a specific date range
3. Search events by title/keyword across single or multiple calendars
4. Filter events to only show future occurrences (after today)
5. Find events without locations, descriptions, or other missing fields
6. Search for events by color code
7. Find all-day events vs timed events

#### Basic Event Updates
8. Bulk rename events (change title for multiple events)
9. Update event descriptions (replace or append text)
10. Add or update event locations
11. Change event colors for visual organization
12. Add Zoom/meeting links to event descriptions
13. Add attendees to multiple events
14. Update event visibility (public/private)

#### Date & Time Adjustments
15. Shift events forward by days/weeks/months (e.g., postpone all meetings by 1 week)
16. Shift events backward (move events earlier)
17. Change start time while keeping duration the same
18. Change end time while keeping start time the same
19. Change both start and end times
20. Adjust times across different timezones
21. Convert event times from one timezone to another

#### Recurring Event Management
22. Convert single events to daily recurring
23. Convert to weekly recurring on specific days (e.g., every Monday and Wednesday)
24. Convert to monthly recurring
25. Set recurrence with end date
26. Set recurrence with occurrence count
27. Update existing recurring event patterns

#### Multi-Calendar Operations
28. Update same event type across multiple calendars (e.g., all team calendars)
29. Sync event changes across personal and work calendars
30. Apply consistent formatting/colors across organization calendars
31. Bulk update events in shared team calendars

#### Event Organization & Cleanup
32. Color-code events by type (meetings=blue, 1:1s=green, interviews=red)
33. Add consistent prefixes/suffixes to event titles
34. Standardize location formats across events
35. Add missing information to incomplete events
36. Archive or update old recurring events

#### Time Management Scenarios
37. Adjust all morning meetings to start 30 minutes later
38. Compress meeting durations (e.g., 60min → 45min for all meetings)
39. Add buffer time between back-to-back meetings
40. Shift all Friday meetings to Thursday
41. Move all afternoon events to morning slots

#### Team & Collaboration
42. Add team meeting links to all recurring team events
43. Update project names across all related events
44. Add status updates or notes to ongoing project meetings
45. Standardize meeting titles for consistency
46. Update contact information in event descriptions

#### Seasonal & Schedule Changes
47. Adjust for daylight saving time changes
48. Update semester/quarter schedules (shift all class times)
49. Accommodate office moves (update all locations)
50. Adjust for remote/hybrid work schedule changes

#### Compliance & Documentation
51. Add required meeting notes templates to descriptions
52. Ensure all client meetings have proper location/link information
53. Add privacy notices or disclaimers to event descriptions
54. Tag events with project codes or billing information

#### Advanced Filtering & Conditional Updates
55. Update only events that match multiple criteria (title AND date range AND no location)
56. Apply different updates to different event types in one script
57. Update events based on attendee count or specific attendees
58. Conditional updates based on event duration
