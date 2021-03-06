from urllib import urlopen
import json
from bs4 import BeautifulSoup
from pre_process import Preprocess


def getBowlerInfo(url):
    webpage = urlopen(url).read()
    soup = BeautifulSoup(webpage, "html5lib")
    data = {}
    data['name'] = Preprocess.preprocess(soup.find(class_='ciPlayernametxt').find('h1').text) \
        .strip()
    for p in soup.find_all(class_='ciPlayerinformationtxt'):
        if 'Bowling style' in p.text:
            data['type'] = Preprocess.preprocess(p.find('span').text)
            break
    return data


def scrapeMatch(dismissal, url):
    print('match : ' + url)
    webpage = urlopen(url).read()
    soup = BeautifulSoup(webpage, "html5lib")
    scorecards = soup.find_all(class_='scorecard-section batsmen')
    if len(scorecards) == 0:
        return False

    player_dismissal = None
    isBreak = False

    wayOut = ""
    player_name = dismissal['batsman']['name']

    i = 0
    for scorecard in scorecards:
        for row in scorecard.find_all(class_='flex-row'):
            if row.find(class_='wrap batsmen'):
                player_name = Preprocess.preprocess(
                    row.find(class_='wrap batsmen').find(class_='cell batsmen').find('a').text)
                nameMatch = False

                if len(dismissal['batsman']['name'].split(" ")) > 1:
                    n = dismissal['batsman']['name'].split(" ")[-1]
                for n2 in player_name.split(" "):
                    if n in n2:
                        nameMatch = True
                        break

                if nameMatch:
                    if row.find(class_='wrap batsmen').find(class_='cell commentary').find('a'):
                        wayOut = Preprocess.preprocess(
                            row.find(class_='wrap batsmen').find(class_='cell commentary') \
                                .find('a').text)
                    else:
                        wayOut = Preprocess.preprocess(
                            row.find(class_='wrap batsmen').find(class_='cell commentary').text
                        )
                    player_dismissal = row.find(class_='content')
                    isBreak = True
                    break
        if isBreak:
            break
        i += 1
    if player_dismissal != None:
        dismissal['bowler'] = {}
        dismissal['scoreAt'] = Preprocess.preprocess(player_dismissal.find_all('span')[1].text).strip()
        dismissal['ball'] = Preprocess.preprocess(player_dismissal.find_all('span')[0].text).strip()

        for s in player_dismissal.find_all('span') :
            s.decompose()
        dismissal['description'] = Preprocess.preprocess(player_dismissal.text).strip()

    if len(scorecards) > 1:
        dismissal['opposition']['total'] = Preprocess.preprocess(scorecards[1 - i] \
                                                                 .find(class_='wrap total') \
                                                                 .find_all('div')[1].text)
    else:
        dismissal['opposition']['total'] = 'DNB'

    dismissal['team']['total'] = Preprocess.preprocess(scorecards[i] \
                                                       .find(class_='wrap total') \
                                                       .find_all('div')[1].text)
    dismissal['bowler'] = {}
    if 'run out' not in wayOut and 'retired hurt' not in wayOut:
        bowler = None
        temp = wayOut.split(" ")
        for t in temp:
            if t.strip() == 'b':
                bowler = temp[temp.index(t) + 1]
        isBreak = False
        if bowler is not None :
            for bowlerSection in soup.find_all(class_='scorecard-section bowling'):
                for link in bowlerSection.find_all('a'):
                    if bowler in link.text:
                        dismissal['bowler'] = getBowlerInfo(link.get('href'))
                        isBreak = True
                        break
                if isBreak:
                    break
    else :
        return False
    return dismissal


def scrapePlayerDismissals(player_name):
    id = 0
    dismissals = []
    webpage = urlopen('http://stats.espncricinfo.com'
                      '/ci/engine/stats/analysis.html?'
                      'search='
                      + ('+'.join(player_name.split(' '))) +
                      ';template=analysis').read()
    soup = BeautifulSoup(webpage, "html5lib")

    player_link = None
    for link in soup.find_all('a'):
        if 'One-Day Internationals player' in link.text:
            player_link = link
            break
    if player_link is not None:
        player_country = Preprocess.preprocess(
            player_link.parent.parent.find_all('td')[1].text
        )

        soup_batsman = BeautifulSoup(urlopen("http://stats.espncricinfo.com" + player_link.get('href')),
                                    "html5lib").find(class_ = 'ciPhotoContainer')

        batsman = {}
        batsman['name'] = player_name
        for p in soup_batsman.find_all('p') :
            if 'right-hand bat' in p.text :
                batsman['batting-hand'] = 'right'
                break
            elif 'left-hand bat' in p.text :
                batsman['batting-hand'] = 'left'
                break

        player_url = player_link.get('href').split(';')[0]
        innings_url = 'http://stats.espncricinfo.com' + player_url + \
                      ';filter=advanced;orderby=start;outs=1;' \
                      'template=results;type=batting;view=innings'

        innings_webpage = urlopen(innings_url)
        innings_html = BeautifulSoup(innings_webpage, "html5lib")

        innings_table = None
        for table in innings_html.find_all(class_='engineTable'):
            if table.find('caption') and \
                            'Innings by innings list' in table.find('caption').text:
                innings_table = table
                break

        for row in innings_table.find('tbody').find_all('tr'):
            dismissal = {}
            dismissal['batsman'] = batsman
            dismissal['player_innings'] = {}
            dismissal['dismissal'] = {}
            dismissal['opposition'] = {}
            dismissal['team'] = {}
            dismissal['team']['country'] = player_country
            i = 1
            for data in row.find_all('td'):
                if i == 1:
                    dismissal['player_innings']['runs'] = Preprocess.preprocess(data.text).strip()
                elif i == 3:
                    dismissal['player_innings']['balls'] = Preprocess.preprocess(data.text).strip()
                elif i == 4:
                    dismissal['player_innings']['4s'] = Preprocess.preprocess(data.text).strip()
                elif i == 5:
                    dismissal['player_innings']['6s'] = Preprocess.preprocess(data.text).strip()
                elif i == 7:
                    dismissal['player_innings']['batting_position'] = Preprocess.preprocess(data.text).strip()
                elif i == 8:
                    dismissal['dismissal']['wayOut'] = Preprocess.preprocess(data.text).strip()
                elif i == 9:
                    dismissal['team_innings'] = Preprocess.preprocess(data.text).strip()
                elif i == 11:
                    dismissal['opposition']['country'] = Preprocess.preprocess(data.find('a').text).strip()
                elif i == 12:
                    dismissal['Stadium'] = Preprocess.preprocess(data.text).strip()
                elif i == 13:
                    dismissal['date'] = Preprocess.preprocess(data.text).strip()
                elif i == 14:
                    scorecard_url = "http://www.espncricinfo.com" + data.find('a').get('href')
                    dismissal = scrapeMatch(dismissal, scorecard_url)
                i += 1
            if dismissal:
                dismissal['id'] = id
                dismissals.append(dismissal)
                id += 1
            print(dismissal)

        with open('Samples/Dismissals/' + '-'.join(player_name.split(" ")) + '-odi-dismissals.json', 'w') as outfile:
            json.dump(dismissals, outfile)

AUS_players = ['Aaron Finch', 'David Warner', 'James Faulkner', 'Matthew Wade',
               'Steven Smith', 'Shaun Marsh']
ENG_players = ['Jos Buttler', 'Eoin Morgan', 'Ben Stokes', 'Jason Roy', 'Chris Woakes',
               'Alex Hales', 'Joe Root']
SL_players = ['Thisara Perera', 'Upul Tharanga', 'Dinesh Chandimal', 'Angelo Mathews',
              'Lahiru Thirimanne', 'Kusal Mendis', 'Kusal Perera']
IND_players = ['Shikhar Dhawan', 'Dinesh Karthik', 'MS Dhoni', 'Ravindra Jadeja',
               'Virat Kohli', 'Ajinkya Rahane', 'RG Sharma', 'Yuvraj Singh']
SA_players = ['AB de Villiers', 'Hashim Amla', 'Quinton de Kock', 'Jean-Paul Duminy',
              'Faf du Plessis', 'David Miller']
NZ_players = ['Kane Williamson', 'Corey Anderson', 'Martin Guptil', 'Tom Latham',
              'Luke Ronchi', 'Ross Taylor']

players = AUS_players + ENG_players + SL_players + IND_players + SA_players + NZ_players

for player in players:
    scrapePlayerDismissals(player)

# dismissal = {
#     "bowler": {},
#     "Stadium": "Rawalpindi",
#     "team_innings": "1",
#     "dismissal": {
#       "wayOut": "run out"
#     },
#     "batsman": {
#       "batting-hand": "right",
#       "name": "Brendon McCullum"
#     },
#     "player_innings": {
#       "runs": "10",
#       "balls": "18",
#       "4s": "1",
#       "6s": "0",
#       "batting_position": "7"
#     },
#     "opposition": {
#       "country": "Pakistan",
#       "total": "184/3 (41.2 Overs, RR: 4.45)"
#     },
#     "team": {
#       "country": "NZ ",
#       "total": "183 all out (47.5 Overs, RR: 3.82)"
#     },
#     "date": "5 Dec 2003"
#   }
# scrapeMatch(dismissal, 'http://www.espncricinfo.com/ci/engine/match/527015.html')
