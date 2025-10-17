"""
Google Calendar Bulk Updater
Allows bulk updates to calendar events based on search criteria
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the token.json file
SCOPES = ['https://www.googleapis.com/auth/calendar']

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
                        f"Credentials file not found at {self.credentials_path}. "
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
    
    def find_events(
        self,
        calendar_id='primary',
        title_contains: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Find events matching criteria
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            title_contains: Filter by title substring
            start_date: Filter events after this date
            end_date: Filter events before this date
            max_results: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=365)
        
        # Format dates for API
        time_min = start_date.isoformat() + 'Z'
        time_max = end_date.isoformat() + 'Z'
        
        print(f"[v0] Searching for events from {start_date.date()} to {end_date.date()}")
        
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
            print(f"[v0] Found {len(events)} events matching '{title_contains}'")
        else:
            print(f"[v0] Found {len(events)} events")
        
        return events
    
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
                print(f"[DRY RUN] Would update '{event_title}' with: {updates}")
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
                    
                    print(f"✓ Updated '{event_title}'")
                    updated_count += 1
                except Exception as e:
                    print(f"✗ Failed to update '{event_title}': {str(e)}")
        
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
            print(f"\nFound {len(events)} events. Running dry run...")
            
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
        else:
            print("No events found matching criteria.")
    
    except FileNotFoundError as e:
        print(f"\n ERROR: {e}")
        print("\nPlease follow setup instructions in README.md")
    except Exception as e:
        print(f"\n ERROR: {e}")
