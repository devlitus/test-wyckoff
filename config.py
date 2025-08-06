import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY')
    
    # Configuraciones de trading
    DEFAULT_SYMBOL = 'BTCUSDT'
    DEFAULT_INTERVAL = '1d'
    DEFAULT_DATA_POINTS = 300
    
    # Configuraciones de análisis
    RSI_PERIOD = 14
    EMA_SHORT = 50
    EMA_LONG = 200
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
