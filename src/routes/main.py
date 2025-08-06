from flask import Blueprint, render_template, request
from src.services.binance_service import get_market_data, filter_current_month_data
from src.services.trend_analysis import detect_trend_changes, add_trend_indicators_to_dataframe
from src.services.wyckoff_service import get_wyckoff_analysis
from binance.client import Client

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    try:
        symbol = 'BTCUSDT'
        interval = Client.KLINE_INTERVAL_1DAY
        data_points = 300
        
        # Obtener datos de mercado
        df = get_market_data(symbol, interval, data_points)
        
        # Filtrar por mes actual
        df_sequence, time_period = filter_current_month_data(df)
        
        # Análisis Wyckoff
        semantic_description = get_wyckoff_analysis(df_sequence)

        # Detectar cambios de tendencia
        trend_changes = detect_trend_changes(df_sequence)
        
        # Crear tabla con indicadores de cambio de tendencia
        df_with_trends = add_trend_indicators_to_dataframe(df_sequence, trend_changes)

        return render_template('index.html',
                             semantic_description=semantic_description,
                             time_period=time_period,
                             df_with_trends=df_with_trends,
                             trend_changes=trend_changes)
    
    except Exception as e:
        return render_template('index.html',
                             semantic_description=f"Error al obtener datos: {str(e)}",
                             time_period="error",
                             df_with_trends=None,
                             trend_changes=None,
                             error=True)
