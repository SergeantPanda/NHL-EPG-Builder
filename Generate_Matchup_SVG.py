import os
import requests
import cairosvg
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
from hashlib import sha256

# Get the directory containing the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

def sanitize_filename(filename, extension):
    """
    Sanitize the filename by removing invalid characters like spaces and periods,
    and append the specified extension.
    """
    invalid_chars = ' .'
    filename = ''.join(c for c in filename if c not in invalid_chars)
    return filename + '.' + extension

def generate_match_svg(away_team_url, home_team_url, output_file_name):
    # Set folder to save SVGs
    output_folder = "logos/"
    # Create the directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Sanitize output file name
    output_file_name = sanitize_filename(output_file_name,'png')

    output_file_path = os.path.join(output_folder, output_file_name)
    
    # Check if the output file already exists and it's not time to replace it yet
    if os.path.exists(output_file_path):
        file_modified_time = os.path.getmtime(output_file_path)
        last_modified_date = datetime.fromtimestamp(file_modified_time)
        current_date = datetime.now()
        # If the file was modified less than a month ago, return the existing file path
        if current_date - last_modified_date < timedelta(days=30):
            print(f"Using cached file: {output_file_name}")
            return output_file_path

    # Generate filename based on URL
    away_team_filename = sha256(away_team_url.encode()).hexdigest()[:10]
    home_team_filename = sha256(home_team_url.encode()).hexdigest()[:10]
    
    # Sanitize team filenames
    away_team_filename = sanitize_filename(away_team_filename,'svg')
    home_team_filename = sanitize_filename(home_team_filename,'svg')

    # Check if the away team SVG file exists and it's not time to replace it yet
    svg_away_team_path = os.path.join(output_folder, away_team_filename)
    if os.path.exists(svg_away_team_path):
        file_modified_time = os.path.getmtime(svg_away_team_path)
        last_modified_date = datetime.fromtimestamp(file_modified_time)
        current_date = datetime.now()
        # If the file was modified less than a month ago, use the cached file
        if current_date - last_modified_date < timedelta(days=30):
            print(f"Using cached file: {away_team_filename}")
            with open(svg_away_team_path, "r") as f:
                svg_away_team = f.read()
        else:
            # Download the away team SVG
            print(f"Downloading and caching file: {away_team_filename}")
            svg_away_team = requests.get(away_team_url).text
            with open(svg_away_team_path, "w") as f:
                f.write(svg_away_team)
    else:
        # Download the away team SVG
        print(f"Downloading and caching file: {away_team_filename}")
        svg_away_team = requests.get(away_team_url).text
        with open(svg_away_team_path, "w") as f:
            f.write(svg_away_team)

    # Check if the home team SVG file exists and it's not time to replace it yet
    svg_home_team_path = os.path.join(output_folder, home_team_filename)
    if os.path.exists(svg_home_team_path):
        file_modified_time = os.path.getmtime(svg_home_team_path)
        last_modified_date = datetime.fromtimestamp(file_modified_time)
        current_date = datetime.now()
        # If the file was modified less than a month ago, use the cached file
        if current_date - last_modified_date < timedelta(days=30):
            print(f"Using cached file: {home_team_filename}")
            with open(svg_home_team_path, "r") as f:
                svg_home_team = f.read()
        else:
            # Download the home team SVG
            print(f"Downloading and caching file: {home_team_filename}")
            svg_home_team = requests.get(home_team_url).text
            with open(svg_home_team_path, "w") as f:
                f.write(svg_home_team)
    else:
        # Download the home team SVG
        print(f"Downloading and caching file: {home_team_filename}")
        svg_home_team = requests.get(home_team_url).text
        with open(svg_home_team_path, "w") as f:
            f.write(svg_home_team)

    svg_center_graphic = open(os.path.join(script_dir, "CenterGraphic.svg"), "r").read()

    # Load the first SVG content
    svg_away_team_content = ET.fromstring(svg_away_team)
    # Load the second SVG content
    svg_home_team_content = ET.fromstring(svg_home_team)
    # Load the center graphic SVG content
    svg_center_graphic_content = ET.fromstring(svg_center_graphic)

    # Calculate the position of the second image relative to the first image
    #view_box = svg_away_team_content.attrib.get('viewBox', '').split()
    #if view_box:
    #    width, height = map(float, view_box[2:])
    #    x2, y2 = width, height

    # Change tag from SVG to G
    svg_away_team_content.tag = 'g'
    svg_home_team_content.tag = 'g'
    svg_center_graphic_content.tag = 'g'

    # Replace 'svg' with 'awayteam' and add transform attribute to the first group
    svg_away_team_content.attrib['id'] = 'awayteam'
    svg_away_team_content.attrib['transform'] = 'translate(0,0) scale(1.25)'
    #svg_away_team_content.attrib['transform'] = 'translate(50,50) scale(1.25)'

    # Replace 'svg' with 'hometeam' and add transform attribute to the second group
    svg_home_team_content.attrib['id'] = 'hometeam'
    svg_home_team_content.attrib['transform'] = f'translate(240,1360) scale(1.25)'
    #svg_home_team_content.attrib['transform'] = f'translate(670,1310) scale(1.25)'

    # Replace 'svg' with 'centergraphic' and add transform attribute to the second group
    svg_center_graphic_content.attrib['id'] = 'centergraphic'
    svg_center_graphic_content.attrib['transform'] = 'translate(208,568) scale(4)'

    # Register NameSpace
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
    # Combine the SVG content
    combined_svg_content = ET.Element('svg', fill="none", viewBox="0 0 1440 2160")

    combined_svg_content.append(svg_away_team_content)
    combined_svg_content.append(svg_home_team_content)
    combined_svg_content.append(svg_center_graphic_content)

    # Prettify the XML
    xml_string = ET.tostring(combined_svg_content, encoding='unicode')
    xml_lines = minidom.parseString(xml_string).toprettyxml(indent="  ").split('\n')
    prettified_xml = '\n'.join([line for line in xml_lines if line.strip()])

    # Convert SVG to PNG with CairoSVG
    cairosvg.svg2png(bytestring=prettified_xml, write_to=output_file_path)

    # Save the combined SVG content to the output file
    #with open(output_file_path, "w") as f:
    #    f.write(prettified_xml)
    
    # Return the output file path
    return output_file_path

# Example usage
#generate_match_svg("https://
