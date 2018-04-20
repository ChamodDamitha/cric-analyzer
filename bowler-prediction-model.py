import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, Dropout
import matplotlib.pyplot as plt
from keras.callbacks import TensorBoard, ReduceLROnPlateau, ModelCheckpoint, EarlyStopping

data = pd.read_csv('Samples/Dismissals/all_dismissals.csv', error_bad_lines=False)
#One hot encoding categoricals
# data = pd.get_dummies(data)

predictors = ['batting-hand', 'innings', 'batsman_runs', 'batsman_balls',
              'batsman_4s', 'batsman_6s', 'batting_position', 'dismissed_ball', 'wickets_fallen', 'runs_scored']

targets = ['bowler_type_way_out']

X = data[predictors]
y = data[targets]
X = pd.get_dummies(X)
y = pd.get_dummies(y)

print(y.columns)

from sklearn.model_selection import train_test_split
train_X, test_X, train_y, test_y = train_test_split(X.as_matrix(), y.as_matrix(), test_size=0.2)
train_X, val_X, train_y, val_y = train_test_split(train_X, train_y, test_size=0.2)

print(train_X.shape)
print(train_y.shape)
print(test_X.shape)
print(test_y.shape)

# create the NN model
model = Sequential()
model.add(Dense(8, input_dim=train_X.shape[1], activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(15, activation='relu'))
# model.add(Dropout(0.25))
# model.add(Dense(5, activation='relu'))
model.add(Dense(train_y.shape[1], activation='softmax'))
#
# compile model
earlyStoper = EarlyStopping(monitor='val_loss', min_delta=0, patience=2, verbose=0, mode='auto')

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
history = model.fit(
    train_X, train_y,
    validation_data=(val_X, val_y),
    nb_epoch=20,
    batch_size=64,
    callbacks=[earlyStoper]
)

# NN model testing
loss, acc = model.test_on_batch(test_X, test_y)
print('Test loss : ' + str(loss))
print('Test accuracy : ' + str(acc))

# sample prediction
train_X = pd.DataFrame(train_X)
print("sample X : " + str(train_X.loc[[0]]))
print("predicted y : " + str(model.predict(train_X.loc[[0]])))

# list all data in history
# print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# ml moodels
# train_y_new = []
# for y in train_y :
#     strr = '';
#     for c in y :
#         strr += str(c);
#     train_y_new.append(int(strr, 2))
# train_y = train_y_new
#
# test_y_new = []
# for y in test_y :
#     strr = '';
#     for c in y :
#         strr += str(c);
#     test_y_new.append(int(strr, 2))
# test_y = test_y_new
#
# from sklearn.metrics import accuracy_score
# from sklearn.naive_bayes import GaussianNB
# gnb = GaussianNB()
#
# gnb.fit(train_X, train_y_new)
# pred_y = gnb.predict(test_X)
# mae = accuracy_score(test_y_new, pred_y)
#
# print("Accuracy score : " + str(mae))