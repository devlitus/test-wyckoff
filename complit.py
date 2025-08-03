import pandas as pd
import numpy as np
from binance.client import Client

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

def get_wyckoff_semantic_translation(df_sequence: pd.DataFrame) -> str:
    """
    Toma una secuencia de 60 velas y la traduce a una descripción semántica
    enfocada en el análisis de Wyckoff.
    """
    # --- Nivel 1: Contexto General de la Secuencia ---
    last_close = df_sequence['close'].iloc[-1]
    last_ema50 = df_sequence['EMA_50'].iloc[-1]
    last_ema200 = df_sequence['EMA_200'].iloc[-1]
    if last_close > last_ema50 and last_ema50 > last_ema200:
        trend_macro = "trend_macro_alcista"
    elif last_close < last_ema50 and last_ema50 < last_ema200:
        trend_macro = "trend_macro_bajista"
    else:
        trend_macro = "trend_macro_lateral"
    max_high = df_sequence['high'].max()
    min_low = df_sequence['low'].min()
    range_size = max_high - min_low
    if df_sequence['close'].std() < (df_sequence['close'].mean() * 0.05):
        structure = f"estructura_en_rango_de_{min_low:.0f}_a_{max_high:.0f}"
    else:
        structure = "estructura_en_tendencia"
    if last_close > min_low + (range_size * 0.66):
        position_in_range = "precio_en_tercio_superior_del_rango"
    elif last_close < min_low + (range_size * 0.33):
        position_in_range = "precio_en_tercio_inferior_del_rango"
    else:
        position_in_range = "precio_en_tercio_medio_del_rango"
    atr_mean = df_sequence['ATR_14'].mean()
    last_atr = df_sequence['ATR_14'].iloc[-1]
    if last_atr > atr_mean * 1.5:
        volatility_profile = "volatilidad_expandiendose"
    elif last_atr < atr_mean * 0.7:
        volatility_profile = "volatilidad_contrayendose"
    else:
        volatility_profile = "volatilidad_normal"
    vol_trend = np.polyfit(range(len(df_sequence)), df_sequence['volume'], 1)[0]
    if vol_trend < -1:
        volume_profile = "volumen_perfil_descendente_secandose"
    elif vol_trend > 1:
        volume_profile = "volumen_perfil_ascendente"
    else:
        volume_profile = "volumen_perfil_plano"
    last_rsi = df_sequence['RSI_14'].iloc[-1]
    if last_rsi > 70:
        rsi_state = "rsi_sobrecompra"
    elif last_rsi < 30:
        rsi_state = "rsi_sobreventa"
    else:
        rsi_state = "rsi_zona_neutral"
    last_candle = df_sequence.iloc[-1]
    volume_mean_20 = df_sequence['volume'].rolling(20).mean().iloc[-1]
    last_candle_desc = ""
    if last_candle['volume'] < volume_mean_20 * 0.5:
        last_candle_desc += "vela_actual_volumen_muy_bajo "
    if last_candle['close'] > last_candle['open']:
        last_candle_desc += "vela_actual_cierre_alcista"
    else:
        last_candle_desc += "vela_actual_cierre_bajista"
    wyckoff_event = "evento_ninguno_detectado"
    support_level = df_sequence['low'].iloc[:-5].min()
    for i in range(1, 6):
        candle = df_sequence.iloc[-i]
        prev_candle = df_sequence.iloc[-i-1]
        if candle['low'] < support_level and candle['close'] > support_level:
            if prev_candle['low'] < support_level:
                wyckoff_event = f"evento_confirmacion_de_spring_en_vela_{-i}"
                break
            else:
                wyckoff_event = f"evento_spring_detectado_en_vela_{-i}"
                break
    final_description_parts = [
        f"asset_BTCUSDT",
        f"interval_personalizado",
        trend_macro,
        structure,
        position_in_range,
        volatility_profile,
        volume_profile,
        rsi_state,
        last_candle_desc.strip(),
        wyckoff_event
    ]
    return " ".join(final_description_parts)

def prepare_data_with_indicators(symbol='BTCUSDT', interval='1h', data_points=300):
    """Descarga datos de Binance y calcula indicadores técnicos"""
    client = Client()
    print(f"Descargando {data_points} velas de {symbol} en temporalidad de {interval}...")
    klines = client.get_klines(symbol=symbol, interval=interval, limit=data_points)
    columns = [
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ]
    df = pd.DataFrame(klines, columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, axis=1)
    df['EMA_50'] = df['close'].ewm(span=50).mean()
    df['EMA_200'] = df['close'].ewm(span=200).mean()
    df['RSI_14'] = calculate_rsi(df['close'], 14)
    df['ATR_14'] = calculate_atr(df, 14)
    return df[['open', 'high', 'low', 'close', 'volume', 'EMA_50', 'EMA_200', 'RSI_14', 'ATR_14']]

if __name__ == "__main__":
    # Puedes cambiar estos parámetros según lo que desees analizar
    symbol = 'BTCUSDT'
    interval = Client.KLINE_INTERVAL_1HOUR  # O usa '1d', '4h', etc.
    data_points = 300
    print("Preparando datos con indicadores técnicos...")
    df = prepare_data_with_indicators(symbol=symbol, interval=interval, data_points=data_points)
    # Tomar las últimas 60 velas para el análisis
    df_sequence = df.tail(60)
    print("Generando traducción semántica...")
    semantic_description = get_wyckoff_semantic_translation(df_sequence)
    print("\n--- TRADUCCIÓN SEMÁNTICA GENERADA ---\n")
    print(semantic_description)
