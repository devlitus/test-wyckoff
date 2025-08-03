from flask import Flask, render_template_string, send_file, request
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from binance.client import Client
from complit import prepare_data_with_indicators, get_wyckoff_semantic_translation

app = Flask(__name__)

@app.route('/trend_chart.png')
def trend_chart():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = Client.KLINE_INTERVAL_1HOUR
    data_points = 60
    df = prepare_data_with_indicators(symbol=symbol, interval=interval, data_points=data_points)
    df['trend'] = np.where(df['close'].diff() > 0, 'up', 'down')
    df['trend_change'] = df['trend'] != df['trend'].shift(1)
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df.index, df['close'], label='Close', color='blue')
    # Marcar canvis de tendència amb creu vermella
    change_points = df[df['trend_change']]
    ax.scatter(change_points.index, change_points['close'], color='red', marker='x', s=80, label='Canvi de tendència')
    ax.set_title('Tancament BTCUSDT amb canvis de tendència')
    ax.set_xlabel('Índex')
    ax.set_ylabel('Preu de tancament')
    ax.legend()
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

app = Flask(__name__)

@app.route('/')
def index():
    symbol = 'BTCUSDT'
    interval = Client.KLINE_INTERVAL_1HOUR
    data_points = 300
    df = prepare_data_with_indicators(symbol=symbol, interval=interval, data_points=data_points)
    df_sequence = df.tail(60)
    semantic_description = get_wyckoff_semantic_translation(df_sequence)
    # Detectar canvis de tendència bàsics: si la direcció del tancament canvia (baixista a alcista o viceversa)
    df_last20 = df_sequence.tail(20).copy()
    df_last20['trend'] = np.where(df_last20['close'].diff() > 0, 'up', 'down')
    df_last20['trend_change'] = df_last20['trend'] != df_last20['trend'].shift(1)
    # Generar la taula HTML amb tooltip quan hi ha canvi de tendència
    table_html = '<table class="table table-striped"><thead><tr>'
    for col in df_last20.columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead><tbody>'
    for i, row in df_last20.iterrows():
        table_html += '<tr>'
        for col in df_last20.columns:
            cell = row[col]
            if col == 'trend' and row['trend_change']:
                # Afegir tooltip a la cel·la de canvi de tendència
                table_html += f'<td><span data-bs-toggle="tooltip" title="Canvi de tendència!">{cell} <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14zm0 1A8 8 0 1 1 8 0a8 8 0 0 1 0 16z"/><path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 .877-.252 1.02-.797.07-.258.106-.438.288-.438.194 0 .234.176.162.438-.146.545-.447.797-.992.797-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.288-.469l-.45-.083.082-.38 2.29-.287c.287-.036.352-.176.288-.469l-.738-3.468c-.194-.897.105-1.319.808-1.319.545 0 .877.252 1.02.797.07.258.106.438.288.438.194 0 .234-.176.162-.438-.146-.545-.447-.797-.992-.797-.703 0-1.002.422-.808 1.319l.738 3.468c.064.293.006.399-.288.469z"/></svg></span></td>'
            else:
                table_html += f'<td>{cell}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    html = f'''
    <html>
    <head>
        <title>Wyckoff Análisis BTCUSDT</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body class="container mt-4">
        <h1 class="mb-4">Wyckoff Análisis BTCUSDT (1h)</h1>
        <h4>Descripción semántica:</h4>
        <div class="alert alert-info">{semantic_description}</div>
        <h4>Gràfica de tancament amb canvis de tendència:</h4>
        <img src="/trend_chart.png?symbol=BTCUSDT" class="img-fluid mb-4" alt="Gràfica de tancament amb canvis de tendència">
        <h4>Últimas 20 velas (con indicadores):</h4>
        {table_html}
        <script>
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {{return new bootstrap.Tooltip(tooltipTriggerEl);}});
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/grafica')
def grafica():
    html = '''
    <html>
    <head>
        <title>Gráfica BTCUSDT - TradingView</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-4">
        <h1 class="mb-4">Gráfica BTCUSDT (TradingView)</h1>
        <div class="mb-4">
            <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_12345&symbol=BINANCE:BTCUSDT&interval=60&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=light&style=1&timezone=Etc/UTC&withdateranges=1&hideideas=1&studies_overrides={}" style="width:100%;height:600px;border:none;"></iframe>
        </div>
        <a href="/" class="btn btn-primary">Tornar a l'inici</a>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
