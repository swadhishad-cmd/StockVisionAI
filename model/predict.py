import joblib
import pandas as pd

# Load trained model
model = joblib.load("saved_models/stock_model.pkl")


def predict_stock(features):
    """
    Feature Order:

    Open
    High
    Low
    Close
    Volume
    MA5
    MA20
    Daily_Return
    RSI
    MACD
    BB_High
    BB_Low
    """

    columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "MA5",
        "MA20",
        "Daily_Return",
        "RSI",
        "MACD",
        "BB_High",
        "BB_Low"
    ]

    data = pd.DataFrame([features], columns=columns)

    prediction = model.predict(data)[0]

    confidence = round(model.predict_proba(data).max() * 100, 2)

    return prediction, confidence