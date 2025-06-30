import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
from io import BytesIO

# Config
st.set_page_config(page_title="Stock Trading Dashboard", layout="wide")
st.title("📈 Buy Low, Sell High - Trading Strategy Dashboard")

# Sidebar
tickers = st.sidebar.multiselect(
    "Select Tickers",
    ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX"],
    default=["AAPL", "MSFT"]
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))
CASH = 10000
POSITION_SIZE = 1

def run_strategy(ticker):
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d")
    if df is None or df.empty or 'Close' not in df.columns:
        return None, None, None

    df.dropna(inplace=True)

    sma = ta.trend.SMAIndicator(close=df['Close'], window=20)
    df['sma20'] = ta.trendSMAIndicator(close=df['Close'], window=20).sma_indicator()

    rsi = ta.momentum.RSIIndicator(close=df['Close'], window=14)
    df['rsi'] = rsi.rsi()

    df['shares'] = 0
    df['cash'] = CASH
    df['portfolio'] = CASH

    in_position = False
    entry_price = 0
    trades = []

    for i in range(20, len(df)):
        price = df.iloc[i]['Close']
        rsi_val = df.iloc[i]['rsi']
        sma_val = df.iloc[i]['sma20']

        if not in_position and rsi_val < 30 and price < sma_val:
            in_position = True
            entry_price = price
            trades.append((df.index[i], "BUY", round(price, 2)))
            df.iloc[i:, df.columns.get_loc('shares')] = POSITION_SIZE
            df.iloc[i:, df.columns.get_loc('cash')] = df.iloc[i]['cash'] - price * POSITION_SIZE

        elif in_position:
            reason = None
            if price <= entry_price * 0.95:
                reason = "STOP-LOSS"
            elif price >= entry_price * 1.10:
                reason = "TAKE-PROFIT"
            elif rsi_val > 70 and price > sma_val:
                reason = "RSI-SELL"

            if reason:
                in_position = False
                trades.append((df.index[i], f"SELL ({reason})", round(price, 2)))
                df.iloc[i:, df.columns.get_loc('shares')] = 0
                df.iloc[i:, df.columns.get_loc('cash')] = df.iloc[i]['cash'] + price * POSITION_SIZE

        df.iloc[i, df.columns.get_loc('portfolio')] = df.iloc[i]['cash'] + df.iloc[i]['shares'] * price

    final = df.iloc[-1]
    stats = {
        "Final Value": round(final['portfolio'], 2),
        "Profit": round(final['portfolio'] - CASH, 2),
        "ROI (%)": round((final['portfolio'] - CASH) / CASH * 100, 2),
        "Last Trade": trades[-1][0] if trades else "None"
    }

    trades_df = pd.DataFrame(trades, columns=["Date", "Action", "Price"])
    return df, stats, trades_df

# Main loop
all_stats = []
all_trades = []

for ticker in tickers:
    st.subheader(f"📊 {ticker}")
    df, stats, trades = run_strategy(ticker)

    if df is None:
        st.warning(f"No data available for {ticker}. Please check the symbol or date range.")
        continue

    st.write(pd.DataFrame([stats], index=[ticker]))
    all_stats.append(stats)
    trades["Ticker"] = ticker
    all_trades.append(trades)

    st.line_chart(df['portfolio'])

    with st.expander("📉 View Price, SMA, RSI"):
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['Close'], label='Price')
        ax.plot(df['sma20'], label='SMA20')
        ax.set_title(f"{ticker} Price vs SMA")
        ax.legend()
        st.pyplot(fig)

        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(df['rsi'], label='RSI', color='orange')
        ax.axhline(30, color='green', linestyle='--')
        ax.axhline(70, color='red', linestyle='--')
        ax.set_title("RSI")
        st.pyplot(fig)

# Show all trades and export
if all_trades:
    st.subheader("📋 All Trades")
    full_trades = pd.concat(all_trades)
    st.dataframe(full_trades)

    # Export to CSV
    csv = full_trades.to_csv(index=False).encode()
    st.download_button(
        label="💾 Export Trades to CSV",
        data=csv,
        file_name="all_trades.csv",
        mime="text/csv"
    )

# Summary
if all_stats:
    st.subheader("📦 Summary Stats")
    st.dataframe(pd.DataFrame(all_stats, index=tickers))
