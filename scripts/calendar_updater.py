"""
Google Calendar Bulk Updater
Allows bulk updates to calendar events based on search criteria
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pytz

# If modifying these scopes, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/calendar']

def load_calendar_config(config_file='calendar_config.json'):
    """Load calendar configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('calendars', [])
    except FileNotFoundError:
        print(f"⚠️ Warning: {config_file} not found. No calendar config loaded.")
        return []
    except json.JSONDecodeError:
        print(f"‼️ Error: {config_file} is not valid JSON.")
        return []

def select_calendars_by_id(calendar_ids, config_file='calendar_config.json'):
    """Select specific calendars from config by their IDs"""
    all_calendars = load_calendar_config(config_file)
    return [cal for cal in all_calendars if cal['id'] in calendar_ids]

def select_calendars_by_name(calendar_names, config_file='calendar_config.json'):
    """Select specific calendars from config by their names"""
    all_calendars = load_calendar_config(config_file)
    return [cal for cal in all_calendars if cal['name'] in calendar_names]


# Use it:
calendars = load_calendar_config()
for cal in calendars:
    print(f"⏳ Processing {cal['name']}: {cal['id']}")

class CalendarUpdater:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        """Initialize the Calendar API client"""
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"‼️ Credentials file not found at {self.credentials_path}. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('calendar', 'v3', credentials=creds)

        def list_calendars(self):
            """List all calendars the user has access to via Google Calendar API"""
            calendar_list = self.service.calendarList().list().execute()
            
            print("\nAccessible Calendars (from Google Calendar API):")
            print("=" * 70)
            for calendar in calendar_list.get('items', []):
                print(f"Name: {calendar['summary']}")
                print(f"ID: {calendar['id']}")
                print(f"Access: {calendar.get('accessRole', 'unknown')}")
                print("-" * 70)
            
            return calendar_list.get('items', [])

    def find_events(
        self,
        calendar_id='primary',
        title_contains: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 100,
        after_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Find events matching criteria
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            title_contains: Filter by title substring
            start_date: Filter events after this date
            end_date: Filter events before this date
            max_results: Maximum number of events to return
            after_date: Only return events after this date (useful for "after today")
        
        Returns:
            List of event dictionaries
        """
        print(f"🔍 Searching calendar: {calendar_id}")

        # Set default date range if not provided
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=365)
        
        # Format dates for API
        time_min = start_date.isoformat() + 'Z'
        time_max = end_date.isoformat() + 'Z'
        
        print(f"🔍 Searching for events from {start_date.date()} to {end_date.date()}")
        
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Filter by title if specified
        if title_contains:
            events = [
                e for e in events 
                if title_contains.lower() in e.get('summary', '').lower()
            ]
            print(f"🔍 Found {len(events)} events matching '{title_contains}' on calendar: {calendar_id}")
        else:
            print(f"🔍 Found {len(events)} events on calendar: {calendar_id}")
        
        if after_date:

            # Make after_date timezone-aware once, before the loop
            if after_date.tzinfo is None:
                after_date_aware = after_date.replace(tzinfo=pytz.UTC)
            else:
                after_date_aware = after_date
            filtered_events = []
            for event in events:
                event_start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
                if event_start:
                    event_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                    if event_dt > after_date_aware:
                        filtered_events.append(event)
            events = filtered_events
            print(f"🔍 Filtered to {len(events)} events after {after_date.date()} on calendar: {calendar_id}")
        
        return events
    
    def shift_event_dates(
        self,
        events: List[Dict],
        calendar_id='primary',
        days: int = 0,
        weeks: int = 0,
        months: int = 0,
        dry_run: bool = True
    ) -> int:
        """
        Shift event dates by specified amount
        
        Args:
            events: List of events to shift
            calendar_id: Calendar ID
            days: Number of days to shift (positive = future, negative = past)
            weeks: Number of weeks to shift
            months: Number of months to shift (approximate: 30 days per month)
            dry_run: If True, only show what would be updated
        
        Returns:
            Number of events updated
        """
        total_days = days + (weeks * 7) + (months * 30)
        shift_delta = timedelta(days=total_days)
        updated_count = 0
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Shifting events by {total_days} days on calendar: {calendar_id}")
        
        for event in events:
            event_id = event['id']
            event_title = event.get('summary', 'Untitled')
            
            try:
                # Get full event details
                full_event = self.service.events().get(
                    calendarId=calendar_id,
                    eventId=event_id
                ).execute()
                
                # Parse start and end times
                start = full_event.get('start', {})
                end = full_event.get('end', {})
                
                # Handle both dateTime and date (all-day events)
                if 'dateTime' in start:
                    start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                    
                    new_start = start_dt + shift_delta
                    new_end = end_dt + shift_delta
                    
                    full_event['start']['dateTime'] = new_start.isoformat()
                    full_event['end']['dateTime'] = new_end.isoformat()
                else:
                    # All-day event
                    start_date = datetime.fromisoformat(start['date'])
                    end_date = datetime.fromisoformat(end['date'])
                    
                    new_start = start_date + shift_delta
                    new_end = end_date + shift_delta
                    
                    full_event['start']['date'] = new_start.date().isoformat()
                    full_event['end']['date'] = new_end.date().isoformat()
                
                if dry_run:
                    print(f"[DRY RUN] Would shift '{event_title}' from {start_dt.date() if 'dateTime' in start else start_date.date()} to {new_start.date()}")
                else:
                    self.service.events().update(
                        calendarId=calendar_id,
                        eventId=event_id,
                        body=full_event
                    ).execute()
                    print(f"✅ Shifted '{event_title}'")
                    updated_count += 1
                    
            except Exception as e:
                print(f"‼️ Failed to shift '{event_title}': {str(e)} on calendar: {calendar_id}")
        
        return updated_count
    
    def adjust_event_times(
        self,
        events: List[Dict],
        calendar_id='primary',
        new_start_time: Optional[str] = None,
        new_end_time: Optional[str] = None,
        timezone: str = 'America/Los_Angeles',
        dry_run: bool = True
    ) -> int:
        """
        Adjust start and/or end times for events while keeping the same date
        
        Args:
            events: List of events to adjust
            calendar_id: Calendar ID
            new_start_time: New start time in HH:MM format (24-hour, e.g., "19:30")
            new_end_time: New end time in HH:MM format (24-hour, e.g., "20:50")
            timezone: Timezone for the events (default: Pacific Time)
            dry_run: If True, only show what would be updated
        
        Returns:
            Number of events updated
        """
        updated_count = 0
        tz = pytz.timezone(timezone)
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Adjusting event times on calendar: {calendar_id}")
        
        for event in events:
            event_id = event['id']
            event_title = event.get('summary', 'Untitled')
            
            try:
                # Get full event details
                full_event = self.service.events().get(
                    calendarId=calendar_id,
                    eventId=event_id
                ).execute()
                
                # Only process events with dateTime (not all-day events)
                start = full_event.get('start', {})
                end = full_event.get('end', {})
                
                if 'dateTime' not in start:
                    print(f"🚫 Skipping all-day event '{event_title}'")
                    continue
                
                # Parse existing times
                start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                
                # Convert to specified timezone
                start_dt = start_dt.astimezone(tz)
                end_dt = end_dt.astimezone(tz)
                
                old_times = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
                
                # Apply new times
                if new_start_time:
                    hour, minute = map(int, new_start_time.split(':'))
                    start_dt = start_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                if new_end_time:
                    hour, minute = map(int, new_end_time.split(':'))
                    end_dt = end_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                new_times = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
                
                # Update event
                full_event['start']['dateTime'] = start_dt.isoformat()
                full_event['end']['dateTime'] = end_dt.isoformat()
                
                if dry_run:
                    print(f"[DRY RUN] Would update '{event_title}' on {start_dt.date()}: {old_times} → {new_times} on calendar: {calendar_id}")
                else:
                    self.service.events().update(
                        calendarId=calendar_id,
                        eventId=event_id,
                        body=full_event
                    ).execute()
                    print(f"✅ Updated '{event_title}' on {start_dt.date()}: {old_times} → {new_times} on calendar: {calendar_id}")
                    updated_count += 1
                    
            except Exception as e:
                print(f"‼️ Failed to adjust '{event_title}': {str(e)} on calendar: {calendar_id}")
        
        return updated_count
    
    def make_recurring(
        self,
        events: List[Dict],
        calendar_id='primary',
        frequency: str = 'WEEKLY',
        interval: int = 1,
        days_of_week: Optional[List[str]] = None,
        until_date: Optional[datetime] = None,
        count: Optional[int] = None,
        dry_run: bool = True
    ) -> int:
        """
        Convert events to recurring events
        
        Args:
            events: List of events to make recurring
            calendar_id: Calendar ID
            frequency: DAILY, WEEKLY, MONTHLY, or YEARLY
            interval: Repeat every N periods (e.g., 2 = every 2 weeks)
            days_of_week: List of days ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
            until_date: Recur until this date
            count: Number of occurrences (alternative to until_date)
            dry_run: If True, only show what would be updated
        
        Returns:
            Number of events updated
        """
        updated_count = 0
        
        # Build recurrence rule
        rrule = f"RRULE:FREQ={frequency};INTERVAL={interval}"
        
        if days_of_week:
            rrule += f";BYDAY={','.join(days_of_week)}"
        
        if until_date:
            until_str = until_date.strftime('%Y%m%dT%H%M%SZ')
            rrule += f";UNTIL={until_str}"
        elif count:
            rrule += f";COUNT={count}"
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Making events recurring with rule: {rrule}")
        
        for event in events:
            event_id = event['id']
            event_title = event.get('summary', 'Untitled')
            
            try:
                # Get full event details
                full_event = self.service.events().get(
                    calendarId=calendar_id,
                    eventId=event_id
                ).execute()
                
                # Add recurrence rule
                full_event['recurrence'] = [rrule]
                
                if dry_run:
                    print(f"[DRY RUN] Would make '{event_title}' recurring")
                else:
                    self.service.events().update(
                        calendarId=calendar_id,
                        eventId=event_id,
                        body=full_event
                    ).execute()
                    print(f"✅ Made '{event_title}' recurring")
                    updated_count += 1
                    
            except Exception as e:
                print(f"‼️ Failed to make '{event_title}' recurring: {str(e)}")
        
        return updated_count

    def bulk_update(
        self,
        events: List[Dict],
        calendar_id='primary',
        new_title: Optional[str] = None,
        new_description: Optional[str] = None,
        new_location: Optional[str] = None,
        new_color_id: Optional[str] = None,
        append_to_description: Optional[str] = None,
        dry_run: bool = True
    ) -> int:
        """
        Bulk update events
        
        Args:
            events: List of events to update
            calendar_id: Calendar ID
            new_title: New title for events
            new_description: New description (replaces existing)
            new_location: New location
            new_color_id: New color ID (1-11)
            append_to_description: Text to append to existing description
            dry_run: If True, only show what would be updated
        
        Returns:
            Number of events updated
        """
        updated_count = 0
        
        for event in events:
            event_id = event['id']
            event_title = event.get('summary', 'Untitled')
            
            # Prepare updates
            updates = {}
            
            if new_title:
                updates['summary'] = new_title
            
            if new_description:
                updates['description'] = new_description
            elif append_to_description:
                existing_desc = event.get('description', '')
                updates['description'] = f"{existing_desc}\n{append_to_description}".strip()
            
            if new_location:
                updates['location'] = new_location
            
            if new_color_id:
                updates['colorId'] = str(new_color_id)
            
            if not updates:
                continue
            
            if dry_run:
                print(f"[DRY RUN] Would update '{event_title}' with: {updates} on calendar: {calendar_id}")
            else:
                try:
                    # Get full event details
                    full_event = self.service.events().get(
                        calendarId=calendar_id,
                        eventId=event_id
                    ).execute()
                    
                    # Apply updates
                    full_event.update(updates)
                    
                    # Update event
                    self.service.events().update(
                        calendarId=calendar_id,
                        eventId=event_id,
                        body=full_event
                    ).execute()
                    
                    print(f"✅ Updated '{event_title}'")
                    updated_count += 1
                except Exception as e:
                    print(f"‼️ Failed to update '{event_title}': {str(e)} on calendar: {calendar_id}")
        
        return updated_count


# Color IDs reference
COLOR_IDS = {
    'lavender': '1',
    'sage': '2',
    'grape': '3',
    'flamingo': '4',
    'banana': '5',
    'tangerine': '6',
    'peacock': '7',
    'graphite': '8',
    'blueberry': '9',
    'basil': '10',
    'tomato': '11'
}


if __name__ == "__main__":
    # Example usage
    print("Google Calendar Bulk Updater")
    print("=" * 50)
    
    try:
        updater = CalendarUpdater()
        
        # Find events with "Meeting" in the title
        events = updater.find_events(
            title_contains="Meeting",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30)
        )
        
        if events:
            print(f"\n🔍 Found {len(events)} events. Running dry run...")
            
            # Dry run - see what would be updated
            updater.bulk_update(
                events,
                append_to_description="Updated via bulk script",
                new_color_id=COLOR_IDS['blueberry'],
                dry_run=True
            )
            
            # Uncomment to actually update:
            # updater.bulk_update(
            #     events,
            #     append_to_description="Updated via bulk script",
            #     new_color_id=COLOR_IDS['blueberry'],
            #     dry_run=False
            # )
            
            # Example of shifting event dates
            # updater.shift_event_dates(
            #     events,
            #     days=7,
            #     dry_run=True
            # )
            
            # Example of adjusting event times
            # updater.adjust_event_times(
            #     events,
            #     new_start_time="10:00",
            #     new_end_time="11:00",
            #     dry_run=True
            # )
            
            # Example of making events recurring
            # updater.make_recurring(
            #     events,
            #     frequency='WEEKLY',
            #     days_of_week=['MO', 'WE'],
            #     dry_run=True
            # )
        else:
            print("‼️ No events found matching criteria.")
    
    except FileNotFoundError as e:
        print(f"\n‼️ Error: {e}")
        print("\nPlease follow setup instructions in README.md")
    except Exception as e:
        print(f"\n‼️ Error: {e}")
