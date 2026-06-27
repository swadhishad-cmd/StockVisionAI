from utils.news import get_stock_news
import plotly.graph_objects as go
from flask import Flask, render_template, request
from model.predict import predict_stock
import yfinance as yf
import ta

app = Flask(__name__)

# ===========================
# Market Overview Stocks
# ===========================
market_symbols = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Google": "GOOGL"
}

# ===========================
# Home Page
# ===========================
@app.route("/")
def home():
    return render_template("index.html")


# ===========================
# Dashboard
# ===========================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    stock_data = None
    prediction = None
    confidence = None
    recommendation = None
    reason = []
    dates = []
    prices = []
    error = None
    chart = None
    news = []
    market_data = []

    # ===========================
    # STOCK SEARCH
    # ===========================
    if request.method == "POST":

        symbol = request.form["symbol"].upper()

        try:
            stock = yf.Ticker(symbol)
            history = stock.history(period="6mo")

            if history.empty:
                error = "Invalid Stock Symbol!"

            else:
                # Fix MultiIndex if any
                if hasattr(history.columns, "levels"):
                    history.columns = history.columns.get_level_values(0)

                # Indicators
                history["MA5"] = history["Close"].rolling(5).mean()
                history["MA20"] = history["Close"].rolling(20).mean()
                history["Daily_Return"] = history["Close"].pct_change()

                history["RSI"] = ta.momentum.RSIIndicator(
                    close=history["Close"]
                ).rsi()

                macd = ta.trend.MACD(close=history["Close"])
                history["MACD"] = macd.macd()

                bb = ta.volatility.BollingerBands(close=history["Close"])
                history["BB_High"] = bb.bollinger_hband()
                history["BB_Low"] = bb.bollinger_lband()

                history.dropna(inplace=True)

                latest = history.iloc[-1]

                # Stock data
                stock_data = {
                    "symbol": symbol,
                    "price": round(latest["Close"], 2),
                    "high": round(latest["High"], 2),
                    "low": round(latest["Low"], 2),
                    "volume": int(latest["Volume"])
                }

                dates = history.index.strftime("%Y-%m-%d").tolist()
                prices = history["Close"].tolist()

                # ===========================
                # CHART (FIXED POSITION)
                # ===========================
                fig = go.Figure(data=[
                    go.Candlestick(
                        x=history.index,
                        open=history["Open"],
                        high=history["High"],
                        low=history["Low"],
                        close=history["Close"],
                        increasing_line_color="#00ff88",
                        decreasing_line_color="#ff4d4d"
                    )
                ])

                fig.update_layout(
                    template="plotly_dark",
                    title=f"{symbol} Stock Price",
                    xaxis_rangeslider_visible=False,
                    height=550,
                    paper_bgcolor="#050816",
                    plot_bgcolor="#050816",
                    font=dict(color="white")
                )

                chart = fig.to_html(full_html=False)

                # ===========================
                # ML FEATURES
                # ===========================
                features = [
                    latest["Open"],
                    latest["High"],
                    latest["Low"],
                    latest["Close"],
                    latest["Volume"],
                    latest["MA5"],
                    latest["MA20"],
                    latest["Daily_Return"],
                    latest["RSI"],
                    latest["MACD"],
                    latest["BB_High"],
                    latest["BB_Low"]
                ]

                prediction, confidence = predict_stock(features)
                confidence = round(confidence * 100, 2)

                recommendation = "BUY 📈" if prediction == 1 else "SELL 📉"

                news = get_stock_news(symbol)

                if prediction == 1:
                    reason = [
                        "Price is above moving average.",
                        "Positive momentum detected.",
                        "Bullish trend confirmed."
                    ]
                else:
                    reason = [
                        "Price is below moving average.",
                        "Weak momentum detected.",
                        "Bearish trend detected."
                    ]

        except Exception as e:
            error = str(e)

    # ===========================
    # MARKET OVERVIEW
    # ===========================
    for company, ticker in market_symbols.items():
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="2d")

            if not history.empty and len(history) >= 2:

                latest_price = round(history["Close"].iloc[-1], 2)
                previous_price = history["Close"].iloc[-2]

                change = round(
                    ((latest_price - previous_price) / previous_price) * 100,
                    2
                )

                market_data.append({
                    "company": company,
                    "ticker": ticker,
                    "price": latest_price,
                    "change": change
                })

        except:
            pass

    return render_template(
        "dashboard.html",
        stock_data=stock_data,
        prediction=prediction,
        confidence=confidence,
        recommendation=recommendation,
        reason=reason,
        dates=dates,
        prices=prices,
        market_data=market_data,
        chart=chart,
        news=news,
        error=error
    )


# ===========================
# Other Pages
# ===========================
@app.route("/predict")
def predict():
    return render_template("predict.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ===========================
# RUN APP
# ===========================
if __name__ == "__main__":
    app.run(debug=True)