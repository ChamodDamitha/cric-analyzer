import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
import matplotlib.pyplot as plt
from keras.callbacks import TensorBoard, ReduceLROnPlateau, ModelCheckpoint, EarlyStopping

data = pd.read_csv('Samples/Dismissals/all_dismissals.csv', error_bad_lines=False)
#One hot encoding categoricals
# data = pd.get_dummies(data)


predictors = ['batting-hand', 'innings', 'batsman_runs', 'batsman_balls',
              'batsman_4s', 'batsman_6s', 'batting_position', 'dismissed_ball', 'wickets_fallen', 'runs_scored']

X = data[predictors]
X = pd.get_dummies(X)
y = data.drop(predictors, axis=1)
y = pd.get_dummies(y)

from sklearn.model_selection import train_test_split
train_X, test_X, train_y, test_y = train_test_split(X.as_matrix(), y.as_matrix(), test_size=0.25)

print(train_X.shape)
print(train_y.shape)
print(test_X.shape)
print(test_y.shape)

# create the model
model = Sequential()
model.add(Dense(8, input_dim=train_X.shape[1], activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(train_y.shape[1], activation='softmax'))

# compile model
earlyStoper = EarlyStopping(monitor='val_loss', min_delta=0, patience=2, verbose=0, mode='auto')

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
history = model.fit(
    train_X, train_y,
    validation_data=(test_X, test_y),
    nb_epoch=10,
    batch_size=64,
    callbacks=[earlyStoper]
)

# list all data in history
print(history.history.keys())
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
