import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    """Calcula el RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_atr(df, period=14):
    """Calcula el Average True Range"""
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def calculate_ema(prices, period):
    """Calcula la Media Móvil Exponencial"""
    return prices.ewm(span=period).mean()

def calculate_sma(prices, period):
    """Calcula la Media Móvil Simple"""
    return prices.rolling(window=period).mean()

def add_technical_indicators(df):
    """
    Añade todos los indicadores técnicos necesarios al DataFrame
    """
    df = df.copy()
    
    # Medias móviles
    df['EMA_50'] = calculate_ema(df['close'], 50)
    df['EMA_200'] = calculate_ema(df['close'], 200)
    df['SMA_20'] = calculate_sma(df['close'], 20)
    
    # RSI
    df['RSI_14'] = calculate_rsi(df['close'], 14)
    
    # ATR
    df['ATR_14'] = calculate_atr(df, 14)
    
    # Volatilidad
    df['volatility'] = df['close'].rolling(window=20).std()
    
    return df
