from urllib import urlopen
import json
from bs4 import BeautifulSoup
from pre_process import Preprocess

dismissals = []

def getBowlerInfo(url) :
    webpage = urlopen(url).read()
    soup = BeautifulSoup(webpage, "html5lib")
    data = {}
    data['name'] = Preprocess.preprocess(soup.find(class_ = 'ciPlayernametxt').find('h1').text)\
        .strip()
    for p in soup.find_all(class_ = 'ciPlayerinformationtxt') :
        if 'Bowling style' in p.text :
            data['type'] = Preprocess.preprocess(p.find('span').text)
            break
    return data


def scrapeMatch(player, country, url, heading):
    print('match : ' + url)
    # url = url.replace('scorecard', 'commentary').strip('/') + '?innings=2&filter=wickets'
    webpage = urlopen(url).read()
    soup = BeautifulSoup(webpage, "html5lib")
    scorecards = soup.find_all(class_='scorecard-section batsmen')

    dismissal = {}
    player_dismissal = 0
    isBreak = False

    wayOut = ""
    player_name = player
    numbers = 0
    i = 0
    for scorecard in scorecards:
        for row in scorecard.find_all(class_='flex-row'):
            if row.find(class_='wrap batsmen'):
                player_name = Preprocess.preprocess(
                    row.find(class_='wrap batsmen').find(class_='cell batsmen').find('a').text)
                if player in player_name:
                    wayOut = row.find(class_='wrap batsmen').find(class_='cell commentary').text
                    if "not out" not in wayOut:
                        wayOut = Preprocess.preprocess(
                            row.find(class_='wrap batsmen').find(class_='cell commentary') \
                                .find('a').text)
                        number_headings_temp = scorecard.find(class_='wrap header').find_all(class_='cell runs')
                        number_headings = [Preprocess.preprocess(x.text) for x in number_headings_temp]
                        numbers = row.find(class_='wrap batsmen').find_all(class_='cell runs')
                        player_dismissal = row.find(class_='content')
                    isBreak = True
                    break
        if isBreak:
            break
        i += 1
    if player_dismissal != 0:
        dismissal['player'] = player_name
        dismissal['player_innings'] = {}
        dismissal['player_innings']['runs'] = Preprocess.preprocess(
            numbers[number_headings.index("R")].text)
        dismissal['player_innings']['balls'] = Preprocess.preprocess(
            numbers[number_headings.index("B")].text)
        dismissal['player_innings']['4s'] = Preprocess.preprocess(
            numbers[number_headings.index("4s")].text)
        dismissal['player_innings']['6s'] = Preprocess.preprocess(
            numbers[number_headings.index("6s")].text)

        # dismissal['venue'] = heading.split("-")[0].split('at')[1].strip()
        dismissal['date'] = heading.split("-")[1].strip()
        dismissal['stadium'] = Preprocess.preprocess(soup.find(class_='stadium-details')
                                                     .find('span').text)
        dismissal['innings'] = i + 1
        dismissal['bowler'] = {}
        dismissal['team'] = {}
        dismissal['opposition'] = {}
        dismissal['team']['country'] = country
        dismissal['wayOut'] = wayOut
        dismissal['scoreAt'] = Preprocess.preprocess(player_dismissal.find_all('span')[1].text).strip()
        dismissal['ball'] = Preprocess.preprocess(player_dismissal.find_all('span')[0].text).strip()
        dismissal['description'] = Preprocess.preprocess(player_dismissal.text).strip()

        countries = heading.split("-")[0].split(":")[1].split("at")[0].split("v")
        for c in countries:
            if country not in c:
                dismissal['opposition']['country'] = c.strip()
                break

        dismissal['opposition']['total'] = Preprocess.preprocess(scorecards[1 - i] \
                                                                 .find(class_='wrap total') \
                                                                 .find_all('div')[1].text)
        dismissal['team']['total'] = Preprocess.preprocess(scorecards[i] \
                                                           .find(class_='wrap total') \
                                                           .find_all('div')[1].text)
        dismissal['bowler'] = {}
        if 'run out' not in wayOut and 'retired hurt' not in wayOut:
            bowler = None
            temp = wayOut.split(" ")
            for t in temp :
                if t.strip() == 'b' :
                    bowler = temp[temp.index(t) + 1]
            isBreak = False
            for bowlerSection in soup.find_all(class_ = 'scorecard-section bowling') :
                for link in bowlerSection.find_all('a') :
                    # print(link.text)
                    if bowler in link.text :
                        dismissal['bowler'] = getBowlerInfo(link.get('href'))
                        isBreak = True
                        break
                if isBreak :
                    break
        print(dismissal)
        dismissals.append(dismissal)


def scrapeSeries(player, country, url):
    print("series : " + url)
    webpage = urlopen(url).read()
    soup = BeautifulSoup(webpage, "html5lib")
    match_summaries = soup.find_all('span', class_='potMatchLink')
    i = 0
    for match in soup.find_all(class_='potMatchMenuLink'):
        if "Scorecard" in match.text:
            match_url = match.get('href')
            country_name = '-'.join(country.lower().strip().split(" "))
            if country_name in match_url:
                scrapeMatch(player, country, match_url,
                            Preprocess.preprocess(match_summaries[i].parent.text))
            i += 1


def scrapeByYear(player, country, year):
    webpage = urlopen(
        "http://www.espncricinfo.com/ci/engine"
        "/series/index.html?season=" + year + ";view=season") \
        .read()

    soup = BeautifulSoup(webpage, "html5lib")
    match_types = soup.find_all(class_='match-section-head')
    all_serieses = soup.find_all(class_='series-summary-wrap')

    # select ODI serieses
    k = 0
    for i in range(len(match_types)):
        if Preprocess.preprocess(match_types[i].find('h2').text) == 'One-Day Internationals':
            k = i
            break
    odi_serieses = all_serieses[k]

    for series in odi_serieses.find_all(class_='series-summary-block'):
        series_url = "http://www.espncricinfo.com" + series.find(class_='teams').find('a').get('href')
        if country in series.find(class_='teams').text \
                or country in series.find(class_='date-location').text:
            scrapeSeries(player, country, series_url)


players = [('Sharma', 'India'), ('Kohli', 'India'), ('Dhoni', 'India'),
           ('Chandimal', 'Sri Lanka'), ('Mathews', 'Sri Lanka'), ('Tharanga', 'Sri Lanka'),
           ('Smith', 'Australia'), ('Warner', 'Australia'), ('Finch', 'Australia')]

for player in players:
    for i in range(2010, 2019):
        scrapeByYear(player[0], player[1], str(i))

    with open(player[0] + '-odi-dismissals-from-2010-2018.json', 'w') as outfile:
        json.dump(dismissals, outfile)

# scrapeMatch("Gambhir", "India",
#             "http://www.espncricinfo.com/series/12457/scorecard/564784/sri-lanka-vs-india-4th-odi/",
#             "1sd : Sri Lanka vs India at Colombo - date_sdfs")
