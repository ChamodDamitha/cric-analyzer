import json
from pprint import pprint
import glob

with open('Samples/Dismissals/all_dismissals.csv', 'wb') as file:
    line = 'batting-hand,bowler_type_way_out,innings,' \
           'batsman_runs,batsman_balls,batsman_4s,batsman_6s,batting_position,' \
           'dismissed_ball,wickets_fallen,runs_scored'
    file.write(line)
    file.write('\n')

for filename in glob.glob('Samples/Dismissals/*.json'):
    print(filename)
    data = json.load(open(filename))
    with open('Samples/Dismissals/all_dismissals.csv', 'a') as file:
        for item in data:
            if ('bowler' in item) and item['bowler'] and ('ball' in item) and ('scoreAt' in item):
                scoreAt = item['scoreAt'].split('/')
                line = item['batsman']['batting-hand'] + ',' + item['bowler']['type'] + '_' + item['dismissal']['wayOut']\
                       + ',' + item['team_innings'] + ',' + \
                       item['player_innings']['runs'] + ',' + item['player_innings']['balls'] \
                       + ',' + item['player_innings']['4s'] + ',' + item['player_innings']['6s'] \
                       + ',' + item['player_innings']['batting_position'] + ',' + item['ball'] \
                       + ',' + str(int(scoreAt[1]) - 1) + ',' + scoreAt[0]
                file.write(line)
                file.write('\n')