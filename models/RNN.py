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

class LSTM:
    def __init__(self, filename: str, layers: int):
        data = pd.read_csv('EURUSD_H1.csv', index_col="Date", parse_dates=True)
        training_set = data.iloc[:,1:2].values
        self.sc = MinMaxScaler(feature_range=(0,1))
        ts_scaled = sc.fit_transform(training_set)

        self.X_train = []
        self.y_train = []
        for i in range(60, 2000):
            self.X_train.append(ts_scaled[i-60:i, 0])
            self.y_train.append(ts_scaled[i, 0])
        self.X_train, self.y_train = np.array(self.X_train), np.array(self.y_train)
        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], self.X_train.shape[1], 1))
        self.layers = layers
        self.__create_model()
        self.__create_test_data()

    def __create_model(self):
        model = Sequential()
        model.add(LSTM(units=STM,return_sequences=True, input_shape=(self.X_train.shape[1], 1)))
        model.add(Dropout(DROPOUT))
        for i in range(0..self.layers):
            model.add(LSTM(units=STM,return_sequences=True))
            model.add(Dropout(DROPOUT))
        model.add(Dense(units=1))
        model.compile(optimizer='adam',loss='mean_squared_error')
        model.fit(self.X_train,self.y_train,epochs=75,batch_size=32)
        self.model = model

    def __create_test_data(self, filename: str):
        test_data = pd.read_csv('AUDUSD_H1.csv', index_col="Date", parse_dates=True)
        real_stock_price = test_data.iloc[:, 1:2].values

        dataset_total = pd.concat((test_data['Open'], test_data['Open']), axis = 0)
        inputs = dataset_total[len(dataset_total) - len(test_data) - 60:].values
        inputs = inputs.reshape(-1,1)
        inputs = self.sc.transform(inputs)
        X_test = []
        for i in range(60, 100000):
            X_test.append(inputs[i-60:i, 0])

        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
        predicted_stock_price = self.model.predict(X_test)
        predicted_stock_price = self.sc.inverse_transform(predicted_stock_price)
        return real_stock_price, predicted_stock_price

    def plot_prediction(self, real_stock_price, predicted_stock_price):
        plt.plot(real_stock_price, color = 'black', label = 'AUDUSD_Real')
        plt.plot(predicted_stock_price, color = 'red', label = 'AUDUSD_Predicted')
        plt.title('AUDUSD Price Prediction')
        plt.xlabel('Time')
        plt.ylabel('AUDUSD Price')
        plt.legend()
        plt.show()
    
    def generate_stock_price(self, last_prices):
        prediction = self.model.predict(last_prices)
        prediction = self.sc.inverse_transform(prediction)