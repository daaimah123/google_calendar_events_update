#!/usr/bin/env python3
"""
Google Calendar Bulk Updater - Interactive CLI
Non-technical user friendly interface for bulk calendar operations
"""

import sys
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from calendar_updater import CalendarUpdater, load_calendar_config
import pytz

# ============================================================================
# ########################## INPUT HELPERS ##########################
# ============================================================================

def prompt_yes_no(question, default='n'):
    """Prompt for yes/no answer"""
    valid = {'y': True, 'yes': True, 'n': False, 'no': False}
    prompt = f"{question} (y/n): "
    
    while True:
        choice = input(prompt).lower().strip()
        if not choice:
            return valid[default]
        if choice in valid:
            return valid[choice]
        print("Please enter 'y' or 'n'")

def prompt_choice(options, prompt_text="Enter choice", multi=False, allow_blank=False):
    """Prompt for numbered choice from list"""
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        if multi:
            choice_input = input(f"\n{prompt_text} (comma-separated): ").strip()
        else:
            choice_input = input(f"\n{prompt_text} (1-{len(options)}): ").strip()
        
        if allow_blank and not choice_input:
            return [] if multi else None
        
        try:
            if multi:
                choices = [int(c.strip()) for c in choice_input.split(',')]
                if all(1 <= c <= len(options) for c in choices):
                    return choices
            else:
                choice = int(choice_input)
                if 1 <= choice <= len(options):
                    return choice
            print(f"Please enter valid number(s) between 1 and {len(options)}")
        except ValueError:
            print("Please enter valid number(s)")

def parse_date_input(user_input, default=None):
    """Parse date input with MM-DD-YYYY format and relative shortcuts"""
    if not user_input.strip():
        return default
    
    user_input = user_input.strip().lower()
    
    # Handle keywords
    if user_input == 'today':
        return datetime.now()
    elif user_input == 'tomorrow':
        return datetime.now() + timedelta(days=1)
    elif user_input == 'yesterday':
        return datetime.now() - timedelta(days=1)
    
    # Handle relative offsets (+7d, -3w, +2m)
    if user_input[0] in ['+', '-']:
        match = re.match(r'([+-]\d+)([dwmy])', user_input)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'd':
                return datetime.now() + timedelta(days=amount)
            elif unit == 'w':
                return datetime.now() + timedelta(weeks=amount)
            elif unit == 'm':
                return datetime.now() + relativedelta(months=amount)
            elif unit == 'y':
                return datetime.now() + relativedelta(years=amount)
    
    # Try MM-DD-YYYY format
    try:
        return datetime.strptime(user_input, '%m-%d-%Y')
    except ValueError:
        raise ValueError(f"Invalid date format: '{user_input}'. Use MM-DD-YYYY, 'today', '+7d', etc.")

def format_date_output(dt_obj):
    """Format datetime as MM-DD-YYYY with day of week"""
    date_str = dt_obj.strftime('%m-%d-%Y')
    day_name = dt_obj.strftime('%A')
    return f"{date_str} ({day_name})"

def format_date_short(dt_obj):
    """Format datetime as MM-DD-YYYY without day of week"""
    return dt_obj.strftime('%m-%d-%Y')

def format_time_12hr(dt_obj):
    """Format time as 12-hour with timezone"""
    time_str = dt_obj.strftime('%I:%M %p').lstrip('0')
    tz_abbr = dt_obj.strftime('%Z')
    return f"{time_str} {tz_abbr}"

def format_event_time_range(start_dt, end_dt):
    """Format event time range in 12-hour format"""
    start_time = start_dt.strftime('%I:%M %p').lstrip('0')
    end_time = end_dt.strftime('%I:%M %p').lstrip('0')
    tz_abbr = start_dt.strftime('%Z')
    return f"{start_time}-{end_time} {tz_abbr}"

def parse_event_datetime(event_time_dict):
    """Parse event start/end time from Google Calendar format"""
    if 'dateTime' in event_time_dict:
        return datetime.fromisoformat(event_time_dict['dateTime'].replace('Z', '+00:00'))
    else:
        # All-day event
        return datetime.strptime(event_time_dict['date'], '%Y-%m-%d')

# ============================================================================
# ########################## DISPLAY HELPERS ##########################
# ============================================================================

def print_header(text):
    """Print section header"""
    print(f"\n{'='*70}")
    print(text)
    print('='*70)

def print_subheader(text):
    """Print subsection header"""
    print(f"\n{text}")
    print('-'*70)

def display_events_by_calendar(events_by_calendar):
    """Display events grouped by calendar"""
    for cal_name, events in events_by_calendar.items():
        print(f"\n{cal_name} - {len(events)} events:")
        for i, event in enumerate(events[:5], 1):  # Show first 5
            start_dt = parse_event_datetime(event['start'])
            end_dt = parse_event_datetime(event['end'])
            time_range = format_event_time_range(start_dt, end_dt)
            date_str = format_date_short(start_dt)
            print(f"  {i}. {event['summary']} - {date_str} {time_range}")
        
        if len(events) > 5:
            print(f"  ... ({len(events) - 5} more)")

def display_events_chronological(all_events):
    """Display events in chronological order"""
    sorted_events = sorted(all_events, key=lambda e: parse_event_datetime(e['start']))
    
    print(f"\nAll Events ({len(sorted_events)} total):")
    for i, event in enumerate(sorted_events[:10], 1):  # Show first 10
        start_dt = parse_event_datetime(event['start'])
        end_dt = parse_event_datetime(event['end'])
        time_range = format_event_time_range(start_dt, end_dt)
        date_str = format_date_short(start_dt)
        cal_name = event.get('_calendar_name', 'Unknown')
        print(f"  {i}. [{cal_name}] {event['summary']} - {date_str} {time_range}")
    
    if len(sorted_events) > 10:
        print(f"  ... ({len(sorted_events) - 10} more)")

def display_events_by_name(all_events):
    """Display events grouped by event name"""
    events_by_name = {}
    for event in all_events:
        name = event['summary']
        if name not in events_by_name:
            events_by_name[name] = []
        events_by_name[name].append(event)
    
    for event_name, events in events_by_name.items():
        print(f"\nEvent: \"{event_name}\" ({len(events)} occurrences)")
        
        # Group by calendar
        by_cal = {}
        for event in events:
            cal_name = event.get('_calendar_name', 'Unknown')
            if cal_name not in by_cal:
                by_cal[cal_name] = []
            by_cal[cal_name].append(event)
        
        for cal_name, cal_events in by_cal.items():
            start_date = format_date_short(parse_event_datetime(cal_events[0]['start']))
            end_date = format_date_short(parse_event_datetime(cal_events[-1]['start']))
            print(f"  {cal_name}: {len(cal_events)} events ({start_date} to {end_date})")

# ============================================================================
# ########################## ANOMALY DETECTION ##########################
# ============================================================================

def detect_recurring_anomalies(events, updater):
    """Detect anomalies in recurring event series"""
    anomalies = []
    
    # Group events by recurring series
    recurring_groups = {}
    for event in events:
        rec_id = event.get('recurringEventId')
        if rec_id:
            if rec_id not in recurring_groups:
                recurring_groups[rec_id] = []
            recurring_groups[rec_id].append(event)
    
    if not recurring_groups:
        return anomalies
    
    # Analyze each series
    for rec_id, series_events in recurring_groups.items():
        if len(series_events) < 3:
            continue  # Need at least 3 to detect pattern
        
        # Determine expected pattern from majority
        days_of_week = {}
        start_times = {}
        durations = {}
        
        for event in series_events:
            start_dt = parse_event_datetime(event['start'])
            end_dt = parse_event_datetime(event['end'])
            
            day = start_dt.strftime('%A')
            days_of_week[day] = days_of_week.get(day, 0) + 1
            
            time = start_dt.time()
            start_times[time] = start_times.get(time, 0) + 1
            
            duration = int((end_dt - start_dt).total_seconds() / 60)
            durations[duration] = durations.get(duration, 0) + 1
        
        # Expected values (most common)
        expected_day = max(days_of_week, key=days_of_week.get)
        expected_time = max(start_times, key=start_times.get)
        expected_duration = max(durations, key=durations.get)
        
        # Check each event for anomalies
        for event in series_events:
            start_dt = parse_event_datetime(event['start'])
            end_dt = parse_event_datetime(event['end'])
            
            actual_day = start_dt.strftime('%A')
            actual_time = start_dt.time()
            actual_duration = int((end_dt - start_dt).total_seconds() / 60)
            
            if actual_day != expected_day:
                anomalies.append({
                    'type': 'DATE_MISMATCH',
                    'event': event,
                    'expected': expected_day,
                    'actual': actual_day,
                    'message': f"Event on {actual_day} instead of {expected_day}"
                })
            
            if actual_time != expected_time:
                exp_time_str = datetime.combine(datetime.today(), expected_time).strftime('%I:%M %p').lstrip('0')
                act_time_str = datetime.combine(datetime.today(), actual_time).strftime('%I:%M %p').lstrip('0')
                anomalies.append({
                    'type': 'TIME_MISMATCH',
                    'event': event,
                    'expected': exp_time_str,
                    'actual': act_time_str,
                    'message': f"Start time is {act_time_str} instead of {exp_time_str}"
                })
            
            if abs(actual_duration - expected_duration) > 5:  # 5 min tolerance
                anomalies.append({
                    'type': 'DURATION_MISMATCH',
                    'event': event,
                    'expected': expected_duration,
                    'actual': actual_duration,
                    'message': f"Duration is {actual_duration} minutes instead of {expected_duration} minutes"
                })
    
    return anomalies

def handle_anomalies(anomalies, all_events):
    """Handle detected anomalies"""
    if not anomalies:
        return all_events
    
    print_subheader("‼️ ANOMALIES DETECTED IN RECURRING SERIES")
    
    # Group anomalies by event
    anomaly_events = {}
    for anomaly in anomalies:
        event_id = anomaly['event']['id']
        if event_id not in anomaly_events:
            anomaly_events[event_id] = []
        anomaly_events[event_id].append(anomaly)
    
    print(f"\n🔍 Found {len(anomalies)} anomalies across {len(anomaly_events)} events\n")
    
    # Show first few anomalies
    for i, (event_id, event_anomalies) in enumerate(list(anomaly_events.items())[:3], 1):
        anomaly = event_anomalies[0]
        event = anomaly['event']
        start_dt = parse_event_datetime(event['start'])
        end_dt = parse_event_datetime(event['end'])
        
        print(f"{i}. {anomaly['type'].replace('_', ' ')}")
        print(f"   Event: {format_date_output(start_dt)} {format_event_time_range(start_dt, end_dt)}")
        print(f"   Calendar: {event.get('_calendar_name', 'Unknown')}")
        print(f"   {anomaly['message']}\n")
    
    if len(anomaly_events) > 3:
        print(f"... ({len(anomaly_events) - 3} more anomalies)\n")
    
    print("How would you like to handle these anomalies?")
    options = [
        "Include all events (anomalies and normal) in update",
        "Exclude anomalies, update only pattern-matching events",
        "Update anomalies separately with different settings",
        "View detailed information about each anomaly",
        "Fix anomalies to match pattern before updating"
    ]
    
    choice = prompt_choice(options, "Enter choice")
    
    if choice == 1:
        print("\nIncluding all events (anomalies and normal)")
        return all_events
    elif choice == 2:
        anomaly_event_ids = set(anomaly_events.keys())
        filtered = [e for e in all_events if e['id'] not in anomaly_event_ids]
        print(f"\nExcluding {len(anomaly_event_ids)} anomalies ({len(filtered)} events remaining)")
        return filtered
    elif choice == 3:
        print("\nSeparate anomaly handling not yet implemented")
        return all_events
    elif choice == 4:
        print("\nDetailed anomaly view not yet implemented")
        return all_events
    elif choice == 5:
        print("\nAutomatic anomaly fixing not yet implemented")
        return all_events

# ============================================================================
# ########################## RECURRING EVENT HANDLING ##########################
# ============================================================================

def handle_recurring_events(events, updater):
    """Handle recurring event series"""
    # Check if events are part of recurring series
    recurring_ids = set()
    for event in events:
        rec_id = event.get('recurringEventId')
        if rec_id:
            recurring_ids.add(rec_id)
    
    if not recurring_ids:
        return events
    
    print_subheader("⚠️ RECURRING EVENT DETECTED")
    
    # Get info about the series
    series_info = {}
    for rec_id in recurring_ids:
        series_events = [e for e in events if e.get('recurringEventId') == rec_id]
        if series_events:
            first_event = series_events[0]
            last_event = series_events[-1]
            series_info[rec_id] = {
                'title': first_event['summary'],
                'count': len(series_events),
                'start_date': parse_event_datetime(first_event['start']),
                'end_date': parse_event_datetime(last_event['start']),
                'events': series_events
            }
    
    for rec_id, info in series_info.items():
        print(f"\nEvent: \"{info['title']}\"")
        print(f"This event is part of a recurring series.")
        print(f"\nCurrent selection includes:")
        print(f"  - {info['count']} individual instances of this recurring event")
        print(f"  - Dates: {format_date_short(info['start_date'])} through {format_date_short(info['end_date'])}")
        
        print("\nWhat would you like to do?")
        options = [
            f"Update only these {info['count']} instances individually",
            "Update the entire recurring series (all past and future)",
            "Update the series from today forward (preserve past instances)",
            "Update the series between specific dates (custom date range)",
            "Skip this recurring event entirely",
            "View more details about the recurrence pattern"
        ]
        
        choice = prompt_choice(options, "Enter choice")
        
        if choice == 1:
            print(f"\nWill update {info['count']} instances individually")
            return events
        elif choice == 2:
            print("\nFull series update not yet implemented")
            return events
        elif choice == 3:
            today = datetime.now()
            filtered = [e for e in info['events'] if parse_event_datetime(e['start']) >= today]
            print(f"\nWill update {len(filtered)} instances from today forward")
            # Replace events with filtered
            other_events = [e for e in events if e.get('recurringEventId') != rec_id]
            return other_events + filtered
        elif choice == 4:
            print("\nEnter the date range for updates:\n")
            start_input = input("Start date (MM-DD-YYYY, 'today', '+7d'): ")
            end_input = input("End date (MM-DD-YYYY, '+30d'): ")
            
            start_date = parse_date_input(start_input, datetime.now())
            end_date = parse_date_input(end_input, datetime.now() + timedelta(days=365))
            
            filtered = [e for e in info['events'] 
                       if start_date <= parse_event_datetime(e['start']) <= end_date]
            
            excluded_before = len([e for e in info['events'] 
                                  if parse_event_datetime(e['start']) < start_date])
            excluded_after = len([e for e in info['events'] 
                                 if parse_event_datetime(e['start']) > end_date])
            
            print(f"\nInstances in range: {len(filtered)} events")
            print(f"  - {format_date_short(start_date)} to {format_date_short(end_date)}")
            print(f"\nInstances outside range (unchanged):")
            print(f"  - Before {format_date_short(start_date)}: {excluded_before} instances")
            print(f"  - After {format_date_short(end_date)}: {excluded_after} instances")
            
            if prompt_yes_no("\nConfirm this date range?"):
                other_events = [e for e in events if e.get('recurringEventId') != rec_id]
                return other_events + filtered
            else:
                return events
        elif choice == 5:
            print("\n🚫 Skipping recurring events")
            return [e for e in events if e.get('recurringEventId') != rec_id]
        elif choice == 6:
            print("\nRecurrence pattern details not yet implemented")
            return events
    
    return events

# ============================================================================
# ########################## MAIN CLI FLOW ##########################
# ============================================================================

def main():
    """Main CLI flow"""
    print_header("Google Calendar Bulk Updater CLI")
    
    # Initialize updater
    updater = CalendarUpdater()
    
    # STEP 1: Select calendars
    print_subheader("STEP 1: Select Calendar(s)")
    
    calendars = load_calendar_config()
    if not calendars:
        print("‼️ No calendars found in calendar_config.json")
        print("Using 'primary' calendar")
        selected_calendars = [{'id': 'primary', 'name': 'Primary Calendar'}]
    else:
        print("\nAvailable calendars from your config:")
        cal_options = [f"{cal['name']} ({cal.get('description', 'No description')})" 
                      for cal in calendars]
        
        selected_indices = prompt_choice(cal_options, "Enter calendar numbers (comma-separated)", multi=True)
        selected_calendars = [calendars[i-1] for i in selected_indices]
        
        print(f"\nSelected: {', '.join([c['name'] for c in selected_calendars])}")
        if not prompt_yes_no("Confirm?"):
            print("Cancelled")
            return
    
    # STEP 2: Define search criteria
    print_subheader("STEP 2: Define Search Criteria")
    
    title_keyword = None
    if prompt_yes_no("\nSearch by title keyword?"):
        title_keyword = input("  Enter keyword: ").strip()
    
    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=365)
    
    if prompt_yes_no("\nFilter by date range?"):
        start_input = input("  Start date (MM-DD-YYYY, 'today', '+7d', or blank for today): ")
        end_input = input("  End date (MM-DD-YYYY, '+30d', or blank for +365 days): ")
        
        start_date = parse_date_input(start_input, start_date)
        end_date = parse_date_input(end_input, end_date)
    
    only_future = prompt_yes_no("\nOnly include future events (after today)?")
    after_date = datetime.now() if only_future else None
    
    max_results_input = input("\nMaximum results per calendar (default 100): ").strip()
    max_results = int(max_results_input) if max_results_input else 100
    
    # Search events
    print(f"\nSearching events from {format_date_short(start_date)} to {format_date_short(end_date)}...")
    
    all_events = []
    events_by_calendar = {}
    
    for calendar in selected_calendars:
        cal_id = calendar['id']
        cal_name = calendar['name']
        
        events = updater.find_events(
            calendar_id=cal_id,
            title_contains=title_keyword,
            start_date=start_date,
            end_date=end_date,
            after_date=after_date,
            max_results=max_results
        )
        
        # Add calendar name to events
        for event in events:
            event['_calendar_name'] = cal_name
        
        all_events.extend(events)
        events_by_calendar[cal_name] = events
    
    if not all_events:
        print("\n‼️ No events found matching criteria")
        return
    
    # STEP 3: Preview events
    print_subheader(f"STEP 3: Preview Found Events ({len(all_events)} events total)")
    
    # Detect anomalies
    print("\nAnalyzing events for recurring patterns...")
    anomalies = detect_recurring_anomalies(all_events, updater)
    
    if anomalies:
        all_events = handle_anomalies(anomalies, all_events)
        if not all_events:
            print("\n‼️ No events remaining after anomaly handling")
            return
    
    # Handle recurring events
    all_events = handle_recurring_events(all_events, updater)
    if not all_events:
        print("\n‼️ No events remaining after recurring event handling")
        return
    
    # Display events
    print("\nHow would you like to view the events?")
    view_options = [
        "Grouped by calendar",
        "Chronological order",
        "Grouped by event name"
    ]
    view_choice = prompt_choice(view_options, "Enter choice")
    
    if view_choice == 1:
        display_events_by_calendar(events_by_calendar)
    elif view_choice == 2:
        display_events_chronological(all_events)
    elif view_choice == 3:
        display_events_by_name(all_events)
    
    if not prompt_yes_no(f"\nContinue with these {len(all_events)} events?"):
        print("Cancelled")
        return
    
    # STEP 4: Select operations
    print_subheader("STEP 4: Select Operation(s)")
    
    print("\nAvailable operations:")
    operation_options = [
        "Update event properties (title, description, location, color)",
        "Shift event dates (move forward/backward by days/weeks/months)",
        "Adjust event times (change start/end times)",
        "Make events recurring"
    ]
    
    selected_ops = prompt_choice(operation_options, "Select operation(s) (comma-separated)", multi=True)
    
    print(f"\nYou selected: {', '.join([operation_options[i-1].split('(')[0].strip() for i in selected_ops])}")
    
    # Configure operations
    operations = []
    
    for op_num in selected_ops:
        if op_num == 3:  # Adjust times
            print_subheader(f"STEP 5: Configure Operation - Adjust Event Times")
            
            # Show example
            if all_events:
                example_event = all_events[0]
                start_dt = parse_event_datetime(example_event['start'])
                end_dt = parse_event_datetime(example_event['end'])
                print(f"\nExample current time: {format_event_time_range(start_dt, end_dt)}")
            
            new_start = input("\nNew start time (HH:MM in 24hr format, blank to keep): ").strip()
            new_end = input("New end time (HH:MM in 24hr format, blank to keep): ").strip()
            timezone = input("Timezone (default America/Los_Angeles): ").strip() or "America/Los_Angeles"
            
            operations.append({
                'type': 'adjust_times',
                'config': {
                    'new_start_time': new_start if new_start else None,
                    'new_end_time': new_end if new_end else None,
                    'timezone': timezone
                }
            })
            
            print("\nConfiguration saved")
    
    if not operations:
        print("\n‼️ No operations configured")
        return
    
    # STEP 6: Dry run
    print_subheader("STEP 6: DRY RUN - Preview Changes")
    
    print("\nRunning dry run to preview changes...\n")
    
    for calendar in selected_calendars:
        cal_name = calendar['name']
        cal_id = calendar['id']
        cal_events = [e for e in all_events if e.get('_calendar_name') == cal_name]
        
        if not cal_events:
            continue
        
        print(f"[DRY RUN] {cal_name}:\n")
        
        for event in cal_events[:3]:  # Show first 3
            start_dt = parse_event_datetime(event['start'])
            end_dt = parse_event_datetime(event['end'])
            
            print(f"  {event['summary']} ({format_date_short(start_dt)})")
            print(f"    Time: {format_event_time_range(start_dt, end_dt)}", end='')
            
            # Apply operations to show preview
            for op in operations:
                if op['type'] == 'adjust_times':
                    config = op['config']
                    if config['new_start_time']:
                        new_start_str = datetime.strptime(config['new_start_time'], '%H:%M').strftime('%I:%M %p').lstrip('0')
                        print(f" → {new_start_str}", end='')
                    if config['new_end_time']:
                        new_end_str = datetime.strptime(config['new_end_time'], '%H:%M').strftime('%I:%M %p').lstrip('0')
                        print(f"-{new_end_str}", end='')
            
            print()
        
        if len(cal_events) > 3:
            print(f"  ... ({len(cal_events) - 3} more events)\n")
    
    print(f"\nSummary: {len(all_events)} events would be updated across {len(selected_calendars)} calendars")
    
    # STEP 7: Confirm
    print_subheader("STEP 7: Confirm Dry Run")
    
    if not prompt_yes_no("\nDoes this look correct?"):
        print("Cancelled")
        return
    
    print("\n👀 IMPORTANT: This will make ACTUAL changes to your Google Calendar.")
    confirm_text = input("Type 'CONFIRM' to proceed: ").strip()
    
    if confirm_text != 'CONFIRM':
        print("Cancelled")
        return
    
    # STEP 8: Execute
    print_subheader("STEP 8: Execute Update")
    
    print("\nUpdating events...\n")
    
    success_count = 0
    failed_count = 0
    
    for calendar in selected_calendars:
        cal_name = calendar['name']
        cal_id = calendar['id']
        cal_events = [e for e in all_events if e.get('_calendar_name') == cal_name]
        
        if not cal_events:
            continue
        
        print(f"Updating {cal_name}...")
        
        for op in operations:
            if op['type'] == 'adjust_times':
                try:
                    updater.adjust_event_times(
                        cal_events,
                        calendar_id=cal_id,
                        new_start_time=op['config']['new_start_time'],
                        new_end_time=op['config']['new_end_time'],
                        timezone=op['config']['timezone'],
                        dry_run=False
                    )
                    success_count += len(cal_events)
                except Exception as e:
                    print(f"  Error: {str(e)}")
                    failed_count += len(cal_events)
    
    # STEP 9: Results
    print_subheader("STEP 9: Results")
    
    print(f"\nFinal Summary:")
    print(f"  Successfully updated: {success_count} events")
    print(f"  Failed: {failed_count} events")
    
    # STEP 10: Next action
    print_subheader("STEP 10: Next Action")
    
    print("\nWhat next?")
    next_options = [
        "Run another operation",
        "List all calendars",
        "Exit"
    ]
    
    next_choice = prompt_choice(next_options, "Enter choice")
    
    if next_choice == 1:
        main()
    elif next_choice == 2:
        updater.list_calendars()
        main()
    else:
        print("\nGoodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
