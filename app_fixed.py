
# Example placeholder content
# Replace this with your original app.py content that had df['close']
# For demonstration, we simulate a basic replacement

import pandas as pd
import ta

def run_strategy(df):
    df['sma20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
    return df

# Example usage
data = pd.DataFrame({'Close': [100, 101, 102, 103, 104]})
result = run_strategy(data)
print(result)
