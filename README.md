# NHL XMLTV Builder

This software is a comprehensive system for building an xmltv file, it will generate png images for game matchups, and extract game schedule information from the NHL website. It consists of three main components:

1. **NHL Schedule Generator**: Python script (`Build XML.py`) for generating an XML TV schedule for NHL games based on scraped data from the NHL website. It utilizes various modules and functions to parse game schedules, convert timezones, and build an XML document in the XMLTV format.

2. **SVG Generation for NHL Matchups**: Python script (`Generate_Matchup_SVG.py`) for generating SVG images for NHL game matchups by combining two team logos with a center graphic. It utilizes web scraping techniques to download, cache, and combine SVG content and then convert it to a PNG image using CairoSVG.

3. **NHL Schedule Extractor**: Python script (`Extract_Schedule_From_NHL.py`) for extracting NHL game schedule information from the NHL website. It utilizes web scraping techniques with the BeautifulSoup library to parse the HTML content and extract relevant data such as game date, time, teams, and networks broadcasting the games.

## Prerequisites

Ensure you have the following installed:

- Python 3.x
- Required Python packages:
  - For NHL XMLTV Generator: `pytz`, `xml.dom.minidom`, `xml.etree.ElementTree`
  - For the Matchup PNG Generation: `requests`, `cairosvg`, `xml.etree.ElementTree`, `xml.dom.minidom`, `hashlib`
  - For NHL Schedule Extractor: `requests`, `beautifulsoup4`, `datetime`

You can install the required packages using pip:

```bash
pip install pytz xml.dom.minidom xml.etree.ElementTree requests cairosvg beautifulsoup4
```

## Usage

Make sure to set the `ICON_BASE_URL` variable inside `Build XML.py` to a location that is accessible by your clients.

Run `Build XML.py` to build your XML. The XML will be saved to the script directory and will be named `nhl_schedule.xml`
