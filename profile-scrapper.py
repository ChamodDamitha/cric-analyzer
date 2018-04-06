from urllib import urlopen
import json
from bs4 import BeautifulSoup
from pre_process import Preprocess


def getPlayersOfCountry(country):
    players = []
    for i in range(26):
        url = "http://www.espncricinfo.com/ci/content/player/country.html?country=" \
              + str(country) + ";alpha=" + chr(65 + i);
        webpage = urlopen(url).read()
        soup = BeautifulSoup(webpage, "html5lib")
        for link in soup.find_all('a', class_="ColumnistSmry"):
            players.append(getPlayerInfo("http://www.espncricinfo.com" + link.get('href')))
        with open('sl-player-profiles' + chr(65 + i) + '.json', 'w') as outfile:
            json.dump(players, outfile)
        players = []

def getPlayerInfo(url):
    # Sending the http request
    webpage = urlopen(url).read()
    # making the soup! yummy ;)
    soup = BeautifulSoup(webpage, "html5lib")

    data = {}
    data['bio'] = {}
    data['statistics'] = {}

    data['bio']['name'] = Preprocess.preprocess(soup.find(class_='ciPlayernametxt').find('h1').text).strip()

    data['bio']['coutry'] = soup.find(class_='PlayersSearchLink').find('b').text

    bio_details = soup.find_all(class_='ciPlayerinformationtxt')
    for det in bio_details:
        data['bio'][det.find('b').text] = Preprocess.preprocess(det.find('span').text).strip()

    stat_tables = soup.find_all(class_='engineTable')
    for table in stat_tables :
        if not table.find('thead') :
            stat_tables.remove(table)

    stat_headings = []
    for head in soup.find_all('span', class_ = 'ciPhotoWidgetLink'):
        stat_headings.append(Preprocess.preprocess(head.text))

    for head in stat_headings:
        if head == "Batting and fielding averages" or head == "Bowling averages" or \
                        head == "Recent matches":
            data['statistics'][head] = {}
        else :
            stat_headings.remove(head)


    for k in range(len(stat_tables)):
        keys = []
        if stat_headings[k] != 'Recent matches' :
            # Batting and bowling
            for col_name in stat_tables[k].find_all('th'):
                key = Preprocess.preprocess(col_name.text)
                if key == '10':
                    key += 'w'
                keys.append(key)
            for row in stat_tables[k].find('tbody').find_all('tr'):
                tds = row.find_all('td')

                if tds[0].find('a'):
                    head = Preprocess.preprocess(tds[0].find('a').find('span').find('b').text)
                else:
                    head = Preprocess.preprocess(tds[0].find('b').text)

                data['statistics'][stat_headings[k]][head] = {}

                for j in range(1, len(tds)):
                    data['statistics'][stat_headings[k]][head][keys[j]] = Preprocess.preprocess(tds[j].text)
        else :
            # recent scores
            for col_name in stat_tables[k].find_all('th'):
                keys.append(Preprocess.preprocess(col_name.text))
            matches = []
            for row in stat_tables[k].find('tbody').find_all('tr'):
                tds = row.find_all('td')
                match = {}
                for i in range(len(tds)):
                    if tds[i].find('a'):
                        d = Preprocess.preprocess(tds[i].find('a').text).replace(' ', '')
                    else:
                        d = Preprocess.preprocess(preprocess(tds[i].text).replace(' ', '')).replace(' ', '')
                    if keys[i] == 'Opposition':
                        d = d.strip('v')
                    match[keys[i]] = d
                matches.append(match)
            data['statistics'][stat_headings[k]] = matches
    return data



getPlayersOfCountry(8)  # country = 8 for Sri Lanka

