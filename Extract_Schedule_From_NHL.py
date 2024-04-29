import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_nhl_schedule():
    url = "https://www.nhl.com/ice/schedulebyweek.htm"
    #url = "https://www.nhl.com/ice/schedulebyday.htm"
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    table_rows = soup.find_all('tr')
    games = []

    for row in table_rows:
        columns = row.find_all('td')
        if columns:
            if 'date' in columns[0].get('class', []):            
                date = columns[0].find(class_='skedStartDateSite').get_text().strip()
                away_team = columns[1].find(class_='teamName').a.get_text().strip()
                away_team_long = columns[1].find(class_='team-logo')['title'].strip()
                away_team_logo = columns[1].find(class_='team-logo')['src'].strip().split('?v=')[0]
                home_team = columns[2].find(class_='teamName').a.get_text().strip()
                home_team_long = columns[2].find(class_='team-logo')['title'].strip()
                home_team_logo = columns[2].find(class_='team-logo')['src'].strip().split('?v=')[0]
                if 'TBD' in columns[3].get_text().strip():
                    print("Stopping schedule builder as the game on " + date + " against " + away_team + " and " + home_team + " is still TBD.")
                    break
                time = columns[3].find(class_='skedStartTimeEST').get_text().strip()
                networks = columns[4].get_text().strip()
                
                game_info = {
                'Date': date,
                'Time': time,
                'AwayTeam': away_team,
                'AwayTeamLong': away_team_long,
                'AwayTeamLogo': away_team_logo,
                'HomeTeam': home_team,
                'HomeTeamLong': home_team_long,
                'HomeTeamLogo': home_team_logo,
                'Network': networks,
                }
                games.append(game_info)
            elif columns and 'team' in columns[0].get('class', []):
                date = datetime.now().strftime("%a %b %d, %Y")
                away_team = columns[0].find(class_='teamName').a.get_text().strip()
                away_team_long = columns[0].find(class_='team-logo')['title'].strip()
                away_team_logo = columns[0].find(class_='team-logo')['src'].strip().split('?v=')[0]
                home_team = columns[1].find(class_='teamName').a.get_text().strip()
                home_team_long = columns[1].find(class_='team-logo')['title'].strip()
                home_team_logo = columns[1].find(class_='team-logo')['src'].strip().split('?v=')[0]
                time = columns[2].find(class_='skedStartTimeEST').get_text().strip()
                networks = columns[3].get_text().strip()

                game_info = {
                    'Date': date,
                    'Time': time,
                    'AwayTeam': away_team,
                    'AwayTeamLong': away_team_long,
                    'AwayTeamLogo': away_team_logo,
                    'HomeTeam': home_team,
                    'HomeTeamLong': home_team_long,
                    'HomeTeamLogo': home_team_logo,
                    'Network': networks,
                }
                games.append(game_info)
    sorted_games = sorted(games, key=lambda x: 'FINAL' not in x['Network'])
    return sorted_games

if __name__ == "__main__":
    games = scrape_nhl_schedule()
    for game in games:
        print("{:<15} {:<10} {:<20} {:<20} {:<10} {:<50} {:<50}".format(
            game['Date'],
            game['Time'],
            game['AwayTeamLong'],
            game['HomeTeamLong'],
            game['Network'],
            game['AwayTeamLogo'],
            game['HomeTeamLogo']
        ))



#sorted_games = sorted(games, key=lambda x: 'FINAL' not in x['Network'])
# Display the scraped game information
#for game in sorted_games:
#    print(f"Date: {game['Date']}, Time: {game['Time']}, Away Team: {game['AwayTeamLong']}, Home Team: {game['HomeTeamLong']}")
