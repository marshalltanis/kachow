import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import os
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Dropout
from scipy.stats import linregress

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error


STM = 100
DROPOUT = 0.1
MODEL_PATH = "./model.keras"

class Model:
    mae_threshold = 0.0012
    rmse_threshold = 0.0018
    r2_threshold = 0.6
    mape_threashold = 0.5
    test_data = "..\\data\\AUDUSD_H1.csv"
    def __init__(self, filename: str, layers: int, recreate: bool):
        data = pd.read_csv(filename, index_col="Date", parse_dates=True)
        training_set = data.iloc[:,1:2].values
        self.sc = MinMaxScaler(feature_range=(0,1))
        ts_scaled = self.sc.fit_transform(training_set)

        self.X_train = []
        self.y_train = []
        for i in range(60, 2000):
            self.X_train.append(ts_scaled[i-60:i, 0])
            self.y_train.append(ts_scaled[i, 0])
        self.X_train, self.y_train = np.array(self.X_train), np.array(self.y_train)
        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], self.X_train.shape[1], 1))
        self.layers = layers

        print("Starting model creation")
        self.__create_model(recreate)

        print("Starting test data creation")
        self.test_data = self.create_test_data(self.test_data)

        print("Evaluating model recall")
        model_ready = self.validate_model(self.test_data[0], self.test_data[1])

        if not model_ready:
            print("Need to tune the model more...")
            return
        print("Saving model")
        self.model.save(MODEL_PATH)

        print("Ready for action")


    def __create_model(self, recreate:bool):
        if os.path.exists(MODEL_PATH) and not recreate:
            print("Found existing model")
            self.model = load_model(MODEL_PATH)
        else:
            print("Creating new model")
            model = Sequential()
            model.add(LSTM(units=STM,return_sequences=True, input_shape=(self.X_train.shape[1], 1)))
            model.add(Dropout(DROPOUT))
            for i in range(1, self.layers-1):
                model.add(LSTM(units=STM,return_sequences=True))
                model.add(Dropout(DROPOUT))
            model.add(LSTM(units=STM, return_sequences=False))

            model.add(Dense(units=1))
            print("Compiling model")
            model.compile(optimizer='adam',loss='mean_squared_error')
            model.fit(self.X_train, self.y_train, epochs=75, batch_size=32, verbose=2)
            self.model = model

    def create_test_data(self, filename: str):
        test_data = pd.read_csv(filename, index_col="Date", parse_dates=True)
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

    def validate_model(self, real_stock_price, predicted_stock_price):
        mae = mean_absolute_error(real_stock_price[:-60], predicted_stock_price)
        mse = mean_squared_error(real_stock_price[:-60], predicted_stock_price)
        rmse = np.sqrt(mse)
        r2 = r2_score(real_stock_price[:-60], predicted_stock_price)
        mape = mean_absolute_percentage_error(real_stock_price[:-60], predicted_stock_price) * 100

        print(f"Mean Absolute Error: {mae} - Mean Absolute Percentage Error: {mape} - Root Mean Squared Error: {rmse} - R-squared: {r2}")

        if rmse >= self.rmse_threshold:
            print(f"RMSE threshold violated: {rmse}")
            return False
        if mape >= self.mape_threashold:
            print(f"MAPE threshold violated: {mape}")
            return False
        if r2 <= self.r2_threshold:
            print(f"R2 threshold violated: {r2}")
            return False
        if mae >= self.mae_threshold:
            print(f"MAE threshold violated: {mae}")
            return False
        return True


    
    def generate_stock_price(self, last_prices):
        prediction = self.model.predict(last_prices)
        prediction = self.sc.inverse_transform(prediction)