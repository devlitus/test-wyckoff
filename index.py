import pandas as pd
from binance.client import Client

# No se necesita API Key ni Secret para datos públicos como los Klines
client = Client()

# --- Parámetros para la descarga de datos ---
symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1DAY # Puedes cambiarlo a '1h', '4h', etc.
data_points = 1000 # Máximo que permite la API por llamada

# --- Descargar los datos desde Binance ---
print(f"Descargando {data_points} velas de {symbol} en temporalidad de {interval}...")
klines = client.get_klines(symbol=symbol, interval=interval, limit=data_points)
print("¡Descarga completa!")

# --- Definir las columnas para el DataFrame ---
# Basado en la documentación de la API de Binance
columns = [
    'timestamp', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
]

# --- Crear y limpiar el DataFrame de Pandas ---
df = pd.DataFrame(klines, columns=columns)

# 1. Convertir el timestamp a un formato de fecha legible
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# 2. Establecer el timestamp como el índice del DataFrame (muy útil para análisis de series temporales)
df.set_index('timestamp', inplace=True)

# 3. Convertir las columnas de precio y volumen a tipos de datos numéricos (float/int)
numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, axis=1)

# 4. Seleccionar solo las columnas que nos interesan para el análisis Wyckoff
wyckoff_df = df[['open', 'high', 'low', 'close', 'volume']]


# --- Mostrar el resultado ---
print("\nPrimeras 5 filas de datos listos para analizar:")
print(wyckoff_df.head())

print("\nÚltimas 5 filas de datos:")
print(wyckoff_df.tail())

print("\nInformación del DataFrame:")
wyckoff_df.info()

# Ahora `wyckoff_df` contiene tus datos OHLCV listos para ser analizados
# El siguiente paso sería visualizarlos y empezar a buscar los eventos de Wyckoff.
# Por ejemplo, con una librería como `mplfinance`.