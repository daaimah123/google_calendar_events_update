"""
Example usage scenarios for the Calendar Updater
"""

from datetime import datetime, timedelta
from calendar_updater import CalendarUpdater, COLOR_IDS


def example_1_update_meeting_titles():
    """Update all 'Team Meeting' events to 'Team Sync'"""
    updater = CalendarUpdater()
    
    events = updater.find_events(
        title_contains="Team Meeting",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=60)
    )
    
    updater.bulk_update(
        events,
        new_title="Team Sync",
        dry_run=True  # Set to False to actually update
    )


def example_2_add_zoom_links():
    """Add Zoom link to all events with 'Remote' in title"""
    updater = CalendarUpdater()
    
    events = updater.find_events(
        title_contains="Remote",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    zoom_link = "\n\nZoom: https://zoom.us/j/your-meeting-id"
    
    updater.bulk_update(
        events,
        append_to_description=zoom_link,
        dry_run=True
    )


def example_3_color_code_events():
    """Color code events by type"""
    updater = CalendarUpdater()
    
    # Make all 1:1 meetings blue
    one_on_ones = updater.find_events(
        title_contains="1:1",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=90)
    )
    
    updater.bulk_update(
        one_on_ones,
        new_color_id=COLOR_IDS['blueberry'],
        dry_run=True
    )
    
    # Make all interviews green
    interviews = updater.find_events(
        title_contains="Interview",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=90)
    )
    
    updater.bulk_update(
        interviews,
        new_color_id=COLOR_IDS['basil'],
        dry_run=True
    )


def example_4_update_location():
    """Update location for all office events"""
    updater = CalendarUpdater()
    
    events = updater.find_events(
        title_contains="Office",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    updater.bulk_update(
        events,
        new_location="123 Main St, Conference Room A",
        dry_run=True
    )


def example_5_custom_search_and_update():
    """Custom example - modify as needed"""
    updater = CalendarUpdater()
    
    # Find events in a specific date range
    events = updater.find_events(
        start_date=datetime(2025, 10, 20),
        end_date=datetime(2025, 10, 27),
        max_results=50
    )
    
    # Filter manually for more complex criteria
    filtered_events = [
        e for e in events 
        if 'project' in e.get('summary', '').lower()
        and e.get('location', '') == ''
    ]
    
    print(f"Found {len(filtered_events)} project events without location")
    
    updater.bulk_update(
        filtered_events,
        new_location="Remote",
        new_color_id=COLOR_IDS['peacock'],
        dry_run=True
    )


def example_6_shift_events_forward():
    """Move all events forward by 1 week"""
    updater = CalendarUpdater()
    
    events = updater.find_events(
        title_contains="Workshop",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    updater.shift_event_dates(
        events,
        weeks=1,  # Move forward 1 week
        dry_run=True
    )


def example_7_adjust_event_times():
    """Change start/end times for specific events"""
    updater = CalendarUpdater()
    
    events = updater.find_events(
        title_contains="Daily Standup",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=60)
    )
    
    # Change to 9:30 AM - 10:00 AM Pacific Time
    updater.adjust_event_times(
        events,
        new_start_time="09:30",
        new_end_time="10:00",
        timezone="America/Los_Angeles",
        dry_run=True
    )


def example_8_make_events_recurring():
    """Convert single events to recurring"""
    updater = CalendarUpdater()
    
    events = updater.find_events(
        title_contains="Team Sync",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=7)
    )
    
    # Make it repeat every Monday and Wednesday for 3 months
    updater.make_recurring(
        events,
        frequency='WEEKLY',
        days_of_week=['MO', 'WE'],
        until_date=datetime.utcnow() + timedelta(days=90),
        dry_run=True
    )


def example_9_project_share_time_adjustment():
    """
    Real use case: Update 'Project Share & Weekly Survey' events
    from 8:00-8:50pm to 7:30-8:50pm Pacific Time for all future events
    """
    updater = CalendarUpdater()
    
    # Find all future "Project Share & Weekly Survey" events
    events = updater.find_events(
        title_contains="Project Share & Weekly Survey",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=365),
        after_date=datetime.utcnow()  # Only events after today
    )
    
    print(f"\nFound {len(events)} future 'Project Share & Weekly Survey' events")
    
    # Adjust times: 7:30 PM - 8:50 PM Pacific
    updater.adjust_event_times(
        events,
        new_start_time="19:30",  # 7:30 PM in 24-hour format
        new_end_time="20:50",    # 8:50 PM in 24-hour format
        timezone="America/Los_Angeles",
        dry_run=True  # Set to False to actually update
    )


def example_10_shift_and_adjust_combo():
    """Combine shifting dates and adjusting times"""
    updater = CalendarUpdater()
    
    # Find events
    events = updater.find_events(
        title_contains="Review Meeting",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # First, shift them forward by 3 days
    updater.shift_event_dates(
        events,
        days=3,
        dry_run=True
    )
    
    # Then adjust the time to 2:00 PM - 3:00 PM
    updater.adjust_event_times(
        events,
        new_start_time="14:00",
        new_end_time="15:00",
        timezone="America/Los_Angeles",
        dry_run=True
    )


if __name__ == "__main__":
    print("Calendar Updater Examples")
    print("=" * 50)
    print("\nUncomment the example you want to run:\n")
    
    # Uncomment one of these to run:
    # example_1_update_meeting_titles()
    # example_2_add_zoom_links()
    # example_3_color_code_events()
    # example_4_update_location()
    # example_5_custom_search_and_update()
    # example_6_shift_events_forward()
    # example_7_adjust_event_times()
    # example_8_make_events_recurring()
    
    # Your specific use case:
    example_9_project_share_time_adjustment()
    
    # example_10_shift_and_adjust_combo()
    
    print("\nRemember to set dry_run=False to actually update events!")
