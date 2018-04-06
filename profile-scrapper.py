from urllib import urlopen
import unicodedata
# Sending the http request
webpage = urlopen('http://www.espncricinfo.com/srilanka/content/player/574178.html').read()

from bs4 import BeautifulSoup

# making the soup! yummy ;)
soup = BeautifulSoup(webpage, "html5lib")

import json


def preprocess(str) :
    try:
        return unicodedata \
            .normalize('NFKD', str) \
            .encode('ascii', 'ignore') \
            .replace('\t', '').replace('\n', '')
    except TypeError:
        return str.replace('\t', '').replace('\n', '')

data = {}
data['bio'] = {}
data['statistics'] = {}

data['bio']['name'] = preprocess(soup.find(class_='ciPlayernametxt').find('h1').text).strip()

data['bio']['coutry'] = soup.find(class_='PlayersSearchLink').find('b').text

bio_details = soup.find_all(class_='ciPlayerinformationtxt')
for det in bio_details:
    data['bio'][det.find('b').text] = preprocess(det.find('span').text).strip()

stat_tables = soup.find_all(class_='engineTable')
del stat_tables[2]
stat_headings = ['Batting', 'Bowling', 'Recent Matches']
for head in stat_headings:
    data['statistics'][head] = {}

for i in range(2):
    keys = []
    for col_name in stat_tables[i].find_all('th'):
        key = preprocess(col_name.text)
        if key == '10':
            key += 'w'
        keys.append(key)
    for row in stat_tables[i].find('tbody').find_all('tr'):
        tds = row.find_all('td')

        if tds[0].find('a'):
            head = preprocess(tds[0].find('a').find('span').find('b').text)
        else:
            head = preprocess(tds[0].find('b').text)

        data['statistics'][stat_headings[i]][head] = {}

        for j in range(1, len(tds)):
            data['statistics'][stat_headings[i]][head][keys[j]] = preprocess(tds[j].text)

# recent scores
keys = []
for col_name in stat_tables[2].find_all('th'):
    keys.append(preprocess(col_name.text))
matches = []
for row in stat_tables[2].find('tbody').find_all('tr'):
    tds = row.find_all('td')
    match = {}
    for i in range(len(tds)):
        if tds[i].find('a'):
            d = preprocess(tds[i].find('a').text).replace(' ', '')
        else :
            d = preprocess(preprocess(tds[i].text).replace(' ', '')).replace(' ', '')
        if keys[i] == 'Opposition' :
            d = d.strip('v')
        match[keys[i]] = d
    matches.append(match)
data['statistics'][stat_headings[2]] = matches
# json_data = json.dumps(data)

#print(data)

with open('player-profile.json', 'w') as outfile:
    json.dump(data, outfile)