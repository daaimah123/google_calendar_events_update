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
    
    print("\nRemember to set dry_run=False to actually update events!")
