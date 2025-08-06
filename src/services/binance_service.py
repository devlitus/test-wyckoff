from binance.client import Client
import pandas as pd
from datetime import datetime, date

def get_market_data(symbol: str, interval: str, data_points: int) -> pd.DataFrame:
    """
    Obtiene datos de mercado de Binance usando la función de complit.py
    """
    try:
        from complit import prepare_data_with_indicators
        
        return prepare_data_with_indicators(
            symbol=symbol, 
            interval=interval, 
            data_points=data_points
        )
    except Exception as e:
        raise Exception(f"Error obteniendo datos de mercado: {str(e)}")

def filter_current_month_data(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Filtra los datos para mostrar solo el mes actual hasta hoy
    """
    # Convertir el índice a datetime si no lo está
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Obtener fecha actual
    today = datetime.now().date()
    current_month = today.month
    current_year = today.year
    
    # Filtrar datos del mes actual hasta el día actual
    df_filtered = df[
        (df.index.month == current_month) & 
        (df.index.year == current_year) & 
        (df.index.date <= today)
    ]
    
    # Si no hay datos del mes actual, usar los últimos 30 días como fallback
    if len(df_filtered) == 0:
        df_filtered = df.tail(30)
        time_period_type = "últimos 30 días (fallback)"
    else:
        time_period_type = f"mes actual hasta hoy"
    
    # Obtener información sobre el período
    if len(df_filtered) > 0:
        start_date = df_filtered.index[0].strftime('%Y-%m-%d')
        end_date = df_filtered.index[-1].strftime('%Y-%m-%d')
        time_period = f"{time_period_type} - {len(df_filtered)} días ({start_date} a {end_date})"
    else:
        time_period = "datos no disponibles"
    
    return df_filtered, time_period
