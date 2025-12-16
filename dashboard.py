import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import os

DATA_FILE = 'crypto_prices_log.csv'

if not os.path.exists(DATA_FILE):
    print(f"CRITICAL ERROR: '{DATA_FILE}' not found. Run crpt.py first.")
    exit()

def load_and_clean_data():
    try:
        df = pd.read_csv(DATA_FILE)
        df_latest = df.tail(10).copy()
        
        clean_cols = ['Price', 'Market_Cap']
        for col in clean_cols:
            df_latest[f'{col}_Cleaned'] = (
                df_latest[col].astype(str)
                .str.replace(r'[$,%]', '', regex=True)
                .replace({'N/A': '0', 'nan': '0'})    
                .astype(float)
            )
        return df_latest
    except Exception as e:
        print(f"Error processing data: {e}")
        return pd.DataFrame()

df_plot = load_and_clean_data()

app = dash.Dash(__name__)

if not df_plot.empty:
    fig = px.bar(
        df_plot,
        x='Name',
        y='Market_Cap_Cleaned',
        title='Top 10 Cryptocurrencies by Market Cap',
        labels={'Market_Cap_Cleaned': 'Market Cap (USD)', 'Name': 'Coin'},
        color='24h_Change',
        hover_data=['Symbol', 'Price', '24h_Change'],
        template='plotly_white'
    )
    timestamp = df_plot["Timestamp"].iloc[-1]
else:
    fig = px.bar(title="No Data Available (Check CSV)")
    timestamp = "N/A"

app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1200px', 'margin': '0 auto'},
    children=[
        html.H1('Crypto Price Tracker', style={'textAlign': 'center', 'color': '#333'}),
        html.Div(f'Last Updated: {timestamp}', style={'textAlign': 'center', 'color': '#777', 'marginBottom': '30px'}),
        dcc.Graph(id='market-cap-graph', figure=fig)
    ]
)

if __name__ == '__main__':
    print("\n--- Launching Dashboard ---")
    print("Open browser to: http://127.0.0.1:8050/")
    app.run(host='0.0.0.0', port=8050, debug=True)