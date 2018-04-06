from urllib import urlopen
import json
from bs4 import BeautifulSoup
from pre_process import Preprocess

def scrapeMatch(player, url):
    url = url.replace('scorecard', 'commentary').strip('/') + '?innings=2&filter=wickets'
    webpage = urlopen(url).read()
    soup = BeautifulSoup(webpage, "html5lib")
    print(soup.title)



def scrapeSeries(player, country, url) :
    webpage = urlopen(url).read()
    soup = BeautifulSoup(webpage, "html5lib")
    for match in soup.find_all(class_ = 'potMatchMenuLink'):
        if "Scorecard" in match.text:
            match_url = match.get('href')
            if country.lower() in match_url :
                scrapeMatch(player, match_url)

def scrapeByYear(player, country, year):
    webpage = urlopen(
        "http://www.espncricinfo.com/ci/engine"
        "/series/index.html?season=" + year + ";view=season")\
        .read()

    soup = BeautifulSoup(webpage, "html5lib")
    match_types = soup.find_all(class_ = 'match-section-head')
    all_serieses = soup.find_all(class_ = 'series-summary-wrap')

    # select ODI serieses
    k = 0
    for i in range(len(match_types)):
        if Preprocess.preprocess(match_types[i].find('h2').text) == 'One-Day Internationals' :
            k = i
            break
    odi_serieses = all_serieses[k]

    indian_serieses = []
    for series in odi_serieses.find_all(class_ = 'series-summary-block') :
        # if 'india' in series.get('data-summary-url'):
        #     indian_serieses.append(series)
        series_url = "http://www.espncricinfo.com" + series.find(class_ = 'teams').find('a').get('href')
        if country in series.find(class_ = 'teams').text\
                or country in series.find(class_ = 'date-location').text :
            scrapeSeries(player, country, series_url)
    # for indian_series in indian_serieses:
    #     for match in indian_series.find(class_ = 'matches-day-block').find('a'):
    #         scrapeMatch(match.get('href'))


scrapeByYear("Kohli", "India", "2015")