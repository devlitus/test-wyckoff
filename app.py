from flask import Flask, render_template_string
import pandas as pd
import numpy as np
from binance.client import Client
from complit import prepare_data_with_indicators, get_wyckoff_semantic_translation

app = Flask(__name__)

@app.route('/')
def index():
    symbol = 'BTCUSDT'
    interval = Client.KLINE_INTERVAL_1HOUR
    data_points = 300
    df = prepare_data_with_indicators(symbol=symbol, interval=interval, data_points=data_points)
    df_sequence = df.tail(60)
    semantic_description = get_wyckoff_semantic_translation(df_sequence)
    table_html = df_sequence.tail(20).to_html(classes='table table-striped', border=0)
    html = f'''
    <html>
    <head>
        <title>Wyckoff Análisis BTCUSDT</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-4">
        <h1 class="mb-4">Wyckoff Análisis BTCUSDT (1h)</h1>
        <h4>Descripción semántica:</h4>
        <div class="alert alert-info">{semantic_description}</div>
        <h4>Últimas 20 velas (con indicadores):</h4>
        {table_html}
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
