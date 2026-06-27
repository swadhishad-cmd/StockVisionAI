import os
import joblib
import yfinance as yf

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from model.preprocess import add_features


# ---------------------------------------
# Download Historical Data
# ---------------------------------------

stock = yf.download(
    "AAPL",
    start="2020-01-01",
    end="2025-01-01"
)

# Flatten MultiIndex columns if present
if hasattr(stock.columns, "levels"):
    stock.columns = stock.columns.get_level_values(0)

data = stock[["Open", "High", "Low", "Close", "Volume"]].copy()
print(data.head())
print(data.dtypes)
# ---------------------------------------
# Feature Engineering
# ---------------------------------------

data = add_features(data)

# Target
data["Target"] = (data["Close"].shift(-1) > data["Close"]).astype(int)

data.dropna(inplace=True)

# ---------------------------------------
# Features
# ---------------------------------------

features = [
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

X = data[features]
y = data["Target"]

# ---------------------------------------
# Train/Test Split
# ---------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ---------------------------------------
# Train Model
# ---------------------------------------

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

model.fit(X_train, y_train)

# ---------------------------------------
# Accuracy
# ---------------------------------------

prediction = model.predict(X_test)

accuracy = accuracy_score(y_test, prediction)

print(f"\nModel Accuracy : {accuracy*100:.2f}%")

# ---------------------------------------
# Save Model
# ---------------------------------------

os.makedirs("saved_models", exist_ok=True)

joblib.dump(model, "saved_models/stock_model.pkl")

print("\n✅ Model Saved Successfully!")