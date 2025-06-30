
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import ta

st.set_page_config(layout="wide")
st.title("📉 Buy Low, Sell High - Trading Strategy Dashboard")

def load_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {e}")
        return pd.DataFrame()

def run_strategy(ticker):
    df = load_data(ticker)
    if df.empty:
        st.warning(f"No data available for {ticker}. Please check the symbol or date range.")
        return df, None, None

    df['sma20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
    df['sma50'] = ta.trend.SMAIndicator(close=df['Close'], window=50).sma_indicator()
    df['Buy'] = (df['sma20'] > df['sma50']) & (df['sma20'].shift(1) <= df['sma50'].shift(1))
    df['Sell'] = (df['sma20'] < df['sma50']) & (df['sma20'].shift(1) >= df['sma50'].shift(1))

    trades = df[(df['Buy']) | (df['Sell'])]
    stats = {
        "Total Buys": int(df['Buy'].sum()),
        "Total Sells": int(df['Sell'].sum())
    }
    return df, stats, trades

def plot_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df['sma20'], mode='lines', name='SMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['sma50'], mode='lines', name='SMA50'))
    fig.add_trace(go.Scatter(x=df.index[df['Buy']], y=df['Close'][df['Buy']], mode='markers', marker=dict(color='green', size=8), name='Buy Signal'))
    fig.add_trace(go.Scatter(x=df.index[df['Sell']], y=df['Close'][df['Sell']], mode='markers', marker=dict(color='red', size=8), name='Sell Signal'))
    fig.update_layout(title=f"{ticker} Price Chart with Buy/Sell Signals", xaxis_title="Date", yaxis_title="Price", height=600)
    st.plotly_chart(fig, use_container_width=True)

# Sidebar
st.sidebar.header("Select Tickers")
tickers = st.sidebar.multiselect("Choose companies", ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"], default=["AAPL"])

# Main display
for ticker in tickers:
    st.subheader(f"📊 {ticker}")
    df, stats, trades = run_strategy(ticker)
    if not df.empty:
        plot_chart(df, ticker)
        if stats:
            st.write("**Strategy Summary:**")
            st.json(stats)
        if trades is not None and not trades.empty:
            st.write("**Trade Log:**")
            st.dataframe(trades.tail(10))
