import pandas as pd
from typing import Dict, List

def detect_trend_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta cambios de tendencia usando múltiples indicadores
    """
    if len(df) < 3:
        return pd.DataFrame()
    
    changes_list = []
    
    for i in range(2, len(df)):
        current_row = df.iloc[i]
        prev_row = df.iloc[i-1]
        prev2_row = df.iloc[i-2]
        
        # Variables para análisis
        current_close = current_row['close']
        prev_close = prev_row['close']
        prev2_close = prev2_row['close']
        
        current_rsi = current_row.get('RSI_14', 50)
        prev_rsi = prev_row.get('RSI_14', 50)
        
        current_ema50 = current_row.get('EMA_50', current_close)
        current_ema200 = current_row.get('EMA_200', current_close)
        
        # Detectar cambios de tendencia
        change_detected = False
        change_type = ""
        change_description = ""
        
        # 1. Cambio de tendencia alcista a bajista
        if (prev2_close < prev_close > current_close and 
            current_close < prev_close * 0.98):
            change_detected = True
            change_type = "Reversión Bajista"
            change_description = "Posible techo formado"
        
        # 2. Cambio de tendencia bajista a alcista
        elif (prev2_close > prev_close < current_close and 
              current_close > prev_close * 1.02):
            change_detected = True
            change_type = "Reversión Alcista"
            change_description = "Posible suelo formado"
        
        # 3. Ruptura de EMA
        elif (prev_close < current_ema50 < current_close):
            change_detected = True
            change_type = "Ruptura EMA50"
            change_description = "Precio rompe EMA50 al alza"
        
        elif (prev_close > current_ema50 > current_close):
            change_detected = True
            change_type = "Ruptura EMA50"
            change_description = "Precio rompe EMA50 a la baja"
        
        # 4. Divergencias RSI
        elif (current_close > prev_close and current_rsi < prev_rsi and prev_rsi > 70):
            change_detected = True
            change_type = "Divergencia Bajista"
            change_description = "Precio sube pero RSI baja (sobrecompra)"
        
        elif (current_close < prev_close and current_rsi > prev_rsi and prev_rsi < 30):
            change_detected = True
            change_type = "Divergencia Alcista"
            change_description = "Precio baja pero RSI sube (sobreventa)"
        
        # 5. Cruce de EMAs
        elif (current_ema50 > current_ema200 and 
              df.iloc[i-1].get('EMA_50', 0) <= df.iloc[i-1].get('EMA_200', 0)):
            change_detected = True
            change_type = "Golden Cross"
            change_description = "EMA50 cruza EMA200 al alza"
        
        elif (current_ema50 < current_ema200 and 
              df.iloc[i-1].get('EMA_50', 0) >= df.iloc[i-1].get('EMA_200', 0)):
            change_detected = True
            change_type = "Death Cross"
            change_description = "EMA50 cruza EMA200 a la baja"
        
        if change_detected:
            changes_list.append({
                'fecha': df.index[i],
                'tipo': change_type,
                'descripcion': change_description,
                'precio': current_close,
                'rsi': current_rsi
            })
    
    if changes_list:
        trend_changes = pd.DataFrame(changes_list)
        trend_changes.set_index('fecha', inplace=True)
        return trend_changes
    
    return pd.DataFrame()

def add_trend_indicators_to_dataframe(df: pd.DataFrame, trend_changes: pd.DataFrame) -> pd.DataFrame:
    """
    Añade indicadores de cambio de tendencia al DataFrame principal
    """
    df_with_trends = df.copy()
    df_with_trends['Cambio_Tendencia'] = ''
    
    for idx, change in trend_changes.iterrows():
        df_with_trends.loc[idx, 'Cambio_Tendencia'] = f"🔄 {change['tipo']} ({change['descripcion']})"
    
    return df_with_trends
