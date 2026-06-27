import ta

def add_features(df):

    df = df.copy()

    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    df["Daily_Return"] = df["Close"].pct_change()

    df["RSI"] = ta.momentum.RSIIndicator(close=df["Close"]).rsi()

    macd = ta.trend.MACD(close=df["Close"])
    df["MACD"] = macd.macd()

    bb = ta.volatility.BollingerBands(close=df["Close"])

    df["BB_High"] = bb.bollinger_hband()
    df["BB_Low"] = bb.bollinger_lband()

    df.dropna(inplace=True)

    return df