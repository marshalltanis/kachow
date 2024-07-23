import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns

from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout

from sklearn.preprocessing import MinMaxScaler

STM = 100
DROPOUT = 0.1

data = pd.read_csv('EURUSD_H1.csv', index_col="Date", parse_dates=True)

training_set = data.iloc[:,1:2].values
sc = MinMaxScaler(feature_range=(0,1))
ts_scaled = sc.fit_transform(training_set)

X_train = []
y_train = []
for i in range(60, 2000):
    X_train.append(ts_scaled[i-60:i, 0])
    y_train.append(ts_scaled[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

model = Sequential()
model.add(LSTM(units=STM,return_sequences=True,input_shape=(X_train.shape[1], 1)))
model.add(Dropout(DROPOUT))
model.add(LSTM(units=STM,return_sequences=True))
model.add(Dropout(DROPOUT))
model.add(LSTM(units=STM,return_sequences=True))
model.add(Dropout(DROPOUT))
model.add(LSTM(units=STM))
model.add(Dropout(DROPOUT))
model.add(Dense(units=1))
model.compile(optimizer='adam',loss='mean_squared_error')
model.fit(X_train,y_train,epochs=75,batch_size=32)

test_data = pd.read_csv('AUDUSD_H1.csv', index_col="Date", parse_dates=True)
real_stock_price = test_data.iloc[:, 1:2].values

dataset_total = pd.concat((test_data['Open'], test_data['Open']), axis = 0)
inputs = dataset_total[len(dataset_total) - len(test_data) - 60:].values
inputs = inputs.reshape(-1,1)
inputs = sc.transform(inputs)

X_test = []
for i in range(60, 100000):
    X_test.append(inputs[i-60:i, 0])

X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
predicted_stock_price = model.predict(X_test)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

print(predicted_stock_price)

plt.plot(real_stock_price, color = 'black', label = 'AUDUSD_Real')
plt.plot(predicted_stock_price, color = 'red', label = 'AUDUSD_Predicted')
plt.title('AUDUSD Price Prediction')
plt.xlabel('Time')
plt.ylabel('AUDUSD Price')
plt.legend()
plt.show()