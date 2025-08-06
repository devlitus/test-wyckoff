from flask import Flask
from config import config
from src.routes.main import main_bp
from src.routes.charts import charts_bp
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(charts_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
