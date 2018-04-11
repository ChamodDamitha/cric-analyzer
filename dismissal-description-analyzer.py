import json
import nltk
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
from pre_process import Preprocess

# def get_default_ball_movement_from_right_hand_batsman(bowler) :
#     bowler = bowler.lower()
#     if 'left' in bowler :
#         if 'chinaman' in bowler :
#             return 'AWAY'
#         else:
#             return 'IN'
#     if 'right' in bowler :
#         return 'IN'
#     if 'legbreak' in bowler :
#         return 'AWAY'

dismissals = json.load(open('Samples/Dismissals/Virat-Kohli-odi-dismissals.json'))

#ball length
# short_keywords = [['short'], ['drags', 'length'], ['holds', 'pitch'], ['bouncer']]
# good_keywords = [['good length']]
# full_keywords = [['full'], ['fuller'], ['tossed'], ['yorker'], ['yorked']]
#
# ball_length = []
# ball_length.append(('SHORT', short_keywords))
# ball_length.append(('GOOD', good_keywords))
# ball_length.append(('FULL', full_keywords))
#
# # ball movement
# into_batsman = [['nips', 'back'], ['comes', 'in'], ['iniswing'], ['iniswinger'], ['iniswinging'] ,['turned', 'in']]
# away_from_batsman = [['moves', 'away'], ['outswing'], ['outswinging'], ['outswinger'], ['turned', 'away'] ]
# hold_line = [['held', 'line']]
#
# ball_movement = []
# ball_movement.append(('INTO_BATSMAN', into_batsman))
# ball_movement.append(('AWAY_FROM_BATSMAN', away_from_batsman))
# ball_movement.append(('HOLD_LINE', hold_line))
#
# def getBallMovement(dismissal) :
#     desc = dismissal['description'].lower()
#     if 'type' in dismissal['bowler'] :
#         ball_hand = get_default_ball_movement(dismissal['bowler']['type'])
#         detectedBallMovment = False
#         if dismissal['dismissal']['wayOut'] != 'run out':
#             for ball_movement_list in ball_movement:
#                 if not detectedBallMovment:
#                     for k in ball_movement_list[1]:
#                         if all(w in desc for w in k):
#                             # text += (ball_movement_list[0] + ", " + desc + "\n")
#                             detectedBallMovment = True
#                             i += 1
#                             break
#             tot += 1
#             if not detectedBallMovment:
#                 text += desc + "\n"
# text = ''
#
# wickets = []
# i = 0
# tot = 0

custom_Sent_tokenizer = PunktSentenceTokenizer()

for dismissal in dismissals:
    if 'description' in dismissal :
        desc = Preprocess.preprocess(dismissal['description'])
        # desc = desc.replace(',', '')
        tokenized = custom_Sent_tokenizer.tokenize(desc)
        for i in tokenized :
            words = nltk.word_tokenize(i)
            tagged = nltk.pos_tag(words)
            print(desc)
            print(tagged)
        break
        # detectedLength = False
        # if dismissal['dismissal']['wayOut'] != 'run out':
        #     for ball_length_list in ball_length:
        #         if not detectedLength:
        #             for k in ball_length_list[1]:
        #                 if all(w in desc for w in k):
        #                     text += (ball_length_list[0] + ", " + desc + "\n")
        #                     detectedLength = True
        #                     i += 1
        #                     break
        #     tot += 1
        #     if not detectedLength:
        #         text += desc + "\n"

#         detectedBallMovment = False
#         if dismissal['dismissal']['wayOut'] != 'run out':
#             for ball_movement_list in ball_movement:
#                 if not detectedBallMovment:
#                     for k in ball_movement_list[1]:
#                         if all(w in desc for w in k):
#                             # text += (ball_movement_list[0] + ", " + desc + "\n")
#                             detectedBallMovment = True
#                             i += 1
#                             break
#             tot += 1
#             if not detectedBallMovment:
#                 text += desc + "\n"
# with open('Samples/Dismissal-descriptions/text.csv', 'w+') as file:
#     file.write(text)
#     file.close()
# print('i = %d tot = %d' % (i, tot))
#
#
