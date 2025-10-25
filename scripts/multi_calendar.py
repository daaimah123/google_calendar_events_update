from datetime import datetime, timedelta
from calendar_updater import CalendarUpdater

def update_project_share_across_calendars():
    """Update Project Share events across multiple calendars"""
    
    updater = CalendarUpdater()
    
    # Your calendars with owner or edit permissions
    calendars = [
        'calA@domain.com',
        'calB@domain.com',
        'calC@domain.com',
        'calD@domain.com'
    ]
    
    total_updated = 0
    
    for calendar_id in calendars:
        print(f"\n{'='*70}")
        print(f"CALENDAR: {calendar_id}")
        print(f"{'='*70}")
        
        try:
            # Find future events
            events = updater.find_events(
                calendar_id=calendar_id,
                title_contains="Project Share & Weekly Survey",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                after_date=datetime.utcnow()
            )
            
            if not events:
                print(f"‼️ No matching events in this calendar")
                continue
            
            # Adjust times from 8:00-8:50pm to 7:30-8:50pm
            count = updater.adjust_event_times(
                events,
                calendar_id=calendar_id,
                new_start_time="19:30",  # 7:30 PM
                new_end_time="20:50",    # 8:50 PM
                timezone="America/Los_Angeles",
                dry_run=True  # Change to False to actually update
            )
            
            total_updated += count
            
        except Exception as e:
            print(f"‼️ Error processing {calendar_id}: {str(e)}")
    
    print(f"\n{'='*70}")
    print(f"SUMMARY: {total_updated} events would be updated across all calendars")
    print(f"{'='*70}")

if __name__ == "__main__":
    update_project_share_across_calendars()