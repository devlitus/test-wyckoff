# Programa de Trading - Análisis de Datos de Binance

Este programa descarga datos históricos de trading de Bitcoin (BTCUSDT) desde la API de Binance y los prepara para análisis técnico usando el método Wyckoff.

## Requisitos

- Python 3.7 o superior
- Conexión a internet para descargar datos de Binance

## Instalación

1. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

1. **Ejecutar el programa:**
   ```bash
   python index.py
   ```

## ¿Qué hace el programa?

1. **Descarga datos:** Obtiene 1000 velas diarias de BTCUSDT desde Binance
2. **Procesa los datos:** Convierte timestamps y tipos de datos
3. **Prepara para análisis:** Crea un DataFrame con datos OHLCV (Open, High, Low, Close, Volume)
4. **Muestra resultados:** Imprime las primeras y últimas filas de datos

## Personalización

Puedes modificar estos parámetros en `index.py`:

- `symbol`: Cambiar el par de trading (ej: 'ETHUSDT', 'ADAUSDT')
- `interval`: Cambiar el timeframe (ej: '1h', '4h', '1w')
- `data_points`: Cambiar la cantidad de velas a descargar (máximo 1000)

## Próximos pasos

El programa prepara los datos para análisis Wyckoff. Puedes:

1. Visualizar los datos usando `mplfinance`
2. Implementar indicadores técnicos
3. Buscar patrones de acumulación/distribución
4. Añadir análisis de volumen

## Dependencias

- `pandas`: Manipulación de datos
- `python-binance`: Cliente para la API de Binance
- `mplfinance`: Visualización de gráficos financieros