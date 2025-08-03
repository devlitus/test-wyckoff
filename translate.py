import pandas as pd
import numpy as np
from binance.client import Client

def get_wyckoff_semantic_translation(df_sequence: pd.DataFrame) -> str:
    """
    Toma una secuencia de 60 velas y la traduce a una descripción semántica
    enfocada en el análisis de Wyckoff.
    """
    
    # --- Nivel 1: Contexto General de la Secuencia ---
    
    # Tendencia Macro
    last_close = df_sequence['close'].iloc[-1]
    last_ema50 = df_sequence['EMA_50'].iloc[-1]
    last_ema200 = df_sequence['EMA_200'].iloc[-1]
    
    if last_close > last_ema50 and last_ema50 > last_ema200:
        trend_macro = "trend_macro_alcista"
    elif last_close < last_ema50 and last_ema50 < last_ema200:
        trend_macro = "trend_macro_bajista"
    else:
        trend_macro = "trend_macro_lateral"

    # Estructura de Rango
    max_high = df_sequence['high'].max()
    min_low = df_sequence['low'].min()
    range_size = max_high - min_low
    
    # Si la desviación estándar es baja en relación al precio, es un rango
    if df_sequence['close'].std() < (df_sequence['close'].mean() * 0.05): # Menos del 5% de desviación
        structure = f"estructura_en_rango_de_{min_low:.0f}_a_{max_high:.0f}"
    else:
        structure = "estructura_en_tendencia"
        
    # Posición en el rango
    if last_close > min_low + (range_size * 0.66):
        position_in_range = "precio_en_tercio_superior_del_rango"
    elif last_close < min_low + (range_size * 0.33):
        position_in_range = "precio_en_tercio_inferior_del_rango"
    else:
        position_in_range = "precio_en_tercio_medio_del_rango"

    # Perfil de Volatilidad (ATR)
    atr_mean = df_sequence['ATR_14'].mean()
    last_atr = df_sequence['ATR_14'].iloc[-1]
    if last_atr > atr_mean * 1.5:
        volatility_profile = "volatilidad_expandiendose"
    elif last_atr < atr_mean * 0.7:
        volatility_profile = "volatilidad_contrayendose"
    else:
        volatility_profile = "volatilidad_normal"

    # Perfil de Volumen
    # Usamos una regresión lineal simple para ver la tendencia del volumen
    vol_trend = np.polyfit(range(len(df_sequence)), df_sequence['volume'], 1)[0]
    if vol_trend < -1: # Pendiente negativa fuerte
        volume_profile = "volumen_perfil_descendente_secandose"
    elif vol_trend > 1:
        volume_profile = "volumen_perfil_ascendente"
    else:
        volume_profile = "volumen_perfil_plano"

    # --- Nivel 2: Indicadores ---
    last_rsi = df_sequence['RSI_14'].iloc[-1]
    if last_rsi > 70:
        rsi_state = "rsi_sobrecompra"
    elif last_rsi < 30:
        rsi_state = "rsi_sobreventa"
    else:
        rsi_state = "rsi_zona_neutral"
    # (La detección de divergencias es más compleja, la omitimos por brevedad)

    # --- Nivel 3 y 4: Eventos Recientes y Wyckoff ---
    
    last_candle = df_sequence.iloc[-1]
    volume_mean_20 = df_sequence['volume'].rolling(20).mean().iloc[-1]
    
    # Describir la última vela
    last_candle_desc = ""
    if last_candle['volume'] < volume_mean_20 * 0.5:
        last_candle_desc += "vela_actual_volumen_muy_bajo "
    if last_candle['close'] > last_candle['open']:
        last_candle_desc += "vela_actual_cierre_alcista"
    else:
        last_candle_desc += "vela_actual_cierre_bajista"
        
    # Lógica para detectar el Spring
    wyckoff_event = "evento_ninguno_detectado"
    support_level = df_sequence['low'].iloc[:-5].min() # Soporte antes de las últimas 5 velas
    
    # Buscamos en las últimas 5 velas
    for i in range(1, 6):
        candle = df_sequence.iloc[-i]
        prev_candle = df_sequence.iloc[-i-1]
        if candle['low'] < support_level and candle['close'] > support_level:
            # ¡Encontramos una recuperación por encima del soporte!
            if prev_candle['low'] < support_level:
                # La vela anterior también estaba por debajo, esto es la confirmación
                wyckoff_event = f"evento_confirmacion_de_spring_en_vela_{-i}"
                break
            else:
                # Esta es la vela del Spring en sí
                wyckoff_event = f"evento_spring_detectado_en_vela_{-i}"
                break

    # --- Ensamblaje Final ---
    
    final_description_parts = [
        f"asset_BTCUSDT", # Podrías pasarlo como argumento
        f"interval_1h",
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

# --- Preparación de Datos ---
def prepare_data_with_indicators():
    """Descarga datos de Binance y calcula indicadores técnicos"""
    client = Client()
    
    # Descargar datos
    symbol = 'BTCUSDT'
    interval = Client.KLINE_INTERVAL_1HOUR
    data_points = 300  # Más datos para calcular indicadores
    
    print(f"Descargando {data_points} velas de {symbol} en temporalidad de {interval}...")
    klines = client.get_klines(symbol=symbol, interval=interval, limit=data_points)
    
    # Crear DataFrame
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
    
    # Calcular indicadores técnicos
    df['EMA_50'] = df['close'].ewm(span=50).mean()
    df['EMA_200'] = df['close'].ewm(span=200).mean()
    df['RSI_14'] = calculate_rsi(df['close'], 14)
    df['ATR_14'] = calculate_atr(df, 14)
    
    return df[['open', 'high', 'low', 'close', 'volume', 'EMA_50', 'EMA_200', 'RSI_14', 'ATR_14']]

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

# --- Ejecución del Ejemplo Completo ---
if __name__ == "__main__":
    print("Preparando datos con indicadores técnicos...")
    df = prepare_data_with_indicators()
    
    # Tomar las últimas 60 velas para el análisis
    df_sequence = df.tail(60)
    
    print("Generando traducción semántica...")
    semantic_description = get_wyckoff_semantic_translation(df_sequence)
    
    print("\n--- TRADUCCIÓN SEMÁNTICA GENERADA ---\n")
    print(semantic_description)