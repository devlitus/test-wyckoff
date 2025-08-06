from complit import get_wyckoff_semantic_translation
import pandas as pd

def get_wyckoff_analysis(df: pd.DataFrame) -> str:
    """
    Wrapper para el análisis Wyckoff - usa la implementación de complit.py
    """
    try:
        return get_wyckoff_semantic_translation(df)
    except Exception as e:
        return f"Error en análisis Wyckoff: {str(e)}"
