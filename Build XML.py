import os
import pytz
import xml.dom.minidom
from Extract_Schedule_From_NHL import scrape_nhl_schedule
from Generate_Matchup_SVG import generate_match_svg
from datetime import datetime, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
ICON_BASE_URL = 'http://ubuntuserver:8088/'
games = scrape_nhl_schedule()

def parse_date_time(date_str, time_str, timezone='America/New_York'):
    try:
        # Attempt to parse the date string in the format '%a %b %d, %Y'
        date = datetime.strptime(date_str, "%a %b %d, %Y")
    except ValueError:
        # If parsing fails, try parsing in the format 'YYYY-MM-DD'
        date = datetime.strptime(date_str, "%Y-%m-%d")

    # Split the time string and remove the timezone abbreviation
    time_parts = time_str.split()
    if 'ET' in time_parts:
        time_parts.remove('ET')
    time_str = ' '.join(time_parts)

    # Parse the time string
    time = datetime.strptime(time_str, "%I:%M %p")
    
    # Combine date and time
    combined = date.replace(hour=time.hour, minute=time.minute)
    
    # Assume the time is in the specified timezone and convert to UTC
    time_zone = pytz.timezone(timezone)
    utc_time = time_zone.localize(combined).astimezone(pytz.utc)
    
    return utc_time

def build_program_element(start_time, duration, channel_id, title, description, icon_url):
    program = Element("programme", start=start_time.strftime("%Y%m%d%H%M%S") + " +0000", stop=(start_time + duration).strftime("%Y%m%d%H%M%S") + " +0000", channel=channel_id)
    title_elem = SubElement(program, "title")
    title_elem.text = title
    desc_elem = SubElement(program, "desc")
    desc_elem.text = description
    icon_elem = SubElement(program, "icon")
    icon_elem.set("src", icon_url)
    return program

def build_xmltv(schedule):
    root = Element("tv")
    root.set("source-info-name", "Panda NHL TV Guide")
    
    # Add channel listings
    for i in range(1, 16):
        channel_id = f"nhl_channel_{i:02}"
        channel_display_name = f"NHL Channel {i}"
        channel_icon_url = "https://a.espncdn.com/i/teamlogos/leagues/500/nhl.png"
        channel = Element("channel", id=channel_id)
        display_name = SubElement(channel, "display-name")
        display_name.text = channel_display_name
        icon = SubElement(channel, "icon")
        icon.set("src", channel_icon_url)
        root.append(channel)
    
    # Dictionary to keep track of channel numbers for each day
    channel_numbers = {}
    # Dictionary to keep track of the last event end time for each channel each day
    last_event_end_times = {}

    # Loop through each game's schedule
    for game in schedule:
        game_date = game['Date']
        event_start_time = parse_date_time(game['Date'], game['Time']).astimezone(pytz.utc)
        
        # Get the channel ID for the game based on the date and time
        channel_id = get_channel_id(event_start_time, channel_numbers)
        
        # Generate upcoming events
        # Convert the UTC start time to Eastern Time
        et_start_time = event_start_time.astimezone(pytz.timezone('America/New_York'))
        #print(et_start_time)
        # Parse game_date to a datetime object
        game_date_datetime = datetime.strptime(game_date, "%a %b %d, %Y")
        # Parse previous_day_str to a datetime object
        previous_day_date = game_date_datetime - timedelta(days=1)

        # Format the previous day date in the expected format
        previous_day_formatted = previous_day_date.strftime("%a %b %d, %Y")

        # Check if there's an event ended program overlapping from the previous day
        last_event_end_time = last_event_end_times.get(previous_day_formatted, {}).get(channel_id)   
        if last_event_end_time and last_event_end_time + timedelta(days=1) > et_start_time:
            # If there's an event ended program overlapping, set the start time after the last event ended
            program_start_time = last_event_end_time.astimezone(pytz.utc)
        else:
            # Otherwise, set the start time to the beginning of the day
            program_start_time = et_start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            program_start_time = program_start_time.astimezone(pytz.utc)
        
        program_title = f"Upcoming: {game['AwayTeamLong']} at {game['HomeTeamLong']} - {et_start_time.strftime('%I:%M %p')} ET"
        program_description = f"Upcoming coverage for {game['AwayTeamLong']} vs {game['HomeTeamLong']}. The game will start at {et_start_time.strftime('%I:%M %p')} ET and will be broadcast on the following channels: {game['Network']}."
        program = build_program_element(program_start_time, event_start_time - program_start_time, channel_id, program_title, program_description, game['Icon'])
        root.append(program)
        
        # Generate the main event program
        event_title = f"Live NHL Hockey: {game['AwayTeamLong']} at {game['HomeTeamLong']}"
        event_description = f"NHL Hockey game between {game['AwayTeamLong']} and {game['HomeTeamLong']}. The game will be broadcast on the following channels: {game['Network']}."
        main_event_icon_url = game.get('Icon', '')  # Assuming the icon URL is in the 'Icon' field
        main_event = build_program_element(event_start_time, timedelta(hours=2, minutes=30), channel_id, event_title, event_description, main_event_icon_url)
        root.append(main_event)
        
        # Generate "event ended" program after each game
        # Determine the end time based on whichever is longer: 5 hours after the event or the start of the next day
        next_day_start = et_start_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        #next_day_start =event_start_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        event_end_time = event_start_time + timedelta(hours=2, minutes=30)

        if next_day_start < event_end_time+ timedelta(hours=5, minutes=00):           
            event_ended_time = event_end_time + timedelta(hours=5, minutes=00)
            #print('next day less than')
        else:           
            event_ended_time = next_day_start.astimezone(pytz.utc)
            #print('next day greater than')
        program_title = f"Event Ended: {game['AwayTeamLong']} VS {game['HomeTeamLong']}"
        program_description = f"The coverage for the NHL game between {game['AwayTeamLong']} and {game['HomeTeamLong']} at {event_end_time.astimezone(pytz.timezone('America/New_York')).strftime('%I:%M %p')} ET has ended. Tune in for the next game on this channel."
        program = build_program_element(event_end_time, event_ended_time - event_end_time, channel_id, program_title, program_description, game['Icon'])
        root.append(program)
        # Update last_event_end_times for the channel of this game
        game_date = game['Date']  
        #print(event_ended_time)
        if game_date not in last_event_end_times:
            last_event_end_times[game_date] = {}
        last_event_end_times[game_date][channel_id] = event_ended_time 
        
    # Check for gaps in schedule and add "no scheduled NHL games" program
    for date, channel_num in channel_numbers.items():
        # Check if there are any games scheduled for the current date
        games_on_date = [game for game in schedule if game['Date'] == date]
        if not games_on_date:            
            # If no games are scheduled, add a program for the entire day
            for channel_id in range(channel_num, 16):
                channel_id_str = f"nhl_channel_{channel_id:02}"
                # Convert date to the desired format
                formatted_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%a %b %d, %Y")
                last_event_end_time = last_event_end_times.get(formatted_date, {}).get(channel_id_str)
                end_of_day = parse_date_time(formatted_date, "12:00 AM")+ timedelta(days=2)
                #print(last_event_end_time)
                start_time = last_event_end_time if last_event_end_time else parse_date_time(date, "12:00 AM")  # Start after the last event if available, otherwise start at midnight
                no_games_title = "No Scheduled NHL Games"
                no_games_description = "There are no scheduled NHL games for today on this channel."
                no_games_program = build_program_element(start_time, end_of_day- start_time, channel_id_str, no_games_title, no_games_description, '')
                root.append(no_games_program)
               
    return root

def get_channel_id(event_start_time, channel_numbers):
    # Determine the channel number based on the event start time
    event_start_time_local = event_start_time.astimezone(pytz.timezone('America/New_York'))
    game_date = event_start_time_local.strftime('%Y-%m-%d')
    
    # Initialize channel number for the day if not already set
    if game_date not in channel_numbers:
        channel_numbers[game_date] = 1
    
    # Generate channel ID based on channel number for the day
    channel_num = channel_numbers[game_date]
    if channel_num > 15:  # Reset to 1 if channel number exceeds 15
        channel_num = 1
    channel_id = f"nhl_channel_{channel_num:02}"  # Format with leading zeros
    
    # Increment channel number for the day
    channel_numbers[game_date] += 1
    
    return channel_id

schedule = []  # Initialize schedule list outside the loop

# Generate schedule for each game and append to the list
for game in games:
    gamelogo = generate_match_svg(game['AwayTeamLogo'],game['HomeTeamLogo'],game['AwayTeam']+'Vs'+game['HomeTeam'])
    schedule.append({
        'Date': game['Date'],
        'Time': game['Time'],
        'AwayTeam': game['AwayTeam'],
        'AwayTeamLong': game['AwayTeamLong'],
        'HomeTeam':  game['HomeTeam'],
        'HomeTeamLong':  game['HomeTeamLong'],
        'Network':  game['Network'],
        'Icon': ICON_BASE_URL+gamelogo
    })

# Write the XML file in a pretty-printed format
xmltv_tree = ElementTree(build_xmltv(schedule))
with open("nhl_schedule.xml", "wb") as f:
    f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')  # Add XML declaration manually
    xmltv_tree.write(f, encoding="utf-8", xml_declaration=False, method="xml", short_empty_elements=False)

# Read the XML file and re-write with pretty-printing
with open("nhl_schedule.xml", "r", encoding="utf-8") as f:
    xml_content = f.read()

dom = xml.dom.minidom.parseString(xml_content)
with open("nhl_schedule.xml", "w", encoding="utf-8") as f:
    f.write(dom.toprettyxml(indent="  ", encoding="utf-8").decode())
