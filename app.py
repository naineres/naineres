import dash

from dash import dcc
from dash import html
from dash import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import os
import time



def load_data():
    data = pd.read_csv("prices.csv", sep=";")
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data

def daily_report(data):
    data['date'] = data['timestamp'].dt.date
    daily_data = data.groupby('date').agg(
        open_price=('price', 'first'),
        close_price=('price', 'last'),
        high_price=('price', 'max'),
        low_price=('price', 'min')
    )
    daily_data['Variation'] = (daily_data['close_price'] - daily_data['open_price']) / daily_data['open_price'] * 100
    daily_data['volatility'] = daily_data['high_price'] - daily_data['low_price']
    return daily_data

app = dash.Dash(__name__)

data = load_data()


app.layout = html.Div(
    children=[
        html.H1(children="Current Matic price"),
        html.H1('Capitalization of 10,173,235,143.95 dollar'),

        html.Div(children="MATIC is Polygon's native cryptocurrency. It is an ERC-20 token, a token created on the Ethereum blockchain. This token is used to govern and secure the Polygon network and pay the network's transaction fees."),
        dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed=data['timestamp'].min().date(),
            max_date_allowed=data['timestamp'].max().date(),
            start_date=data['timestamp'].min().date(),
            end_date=data['timestamp'].max().date()
        ),
        dcc.Graph(id="live-update-graph"),
        dcc.Interval(
            id="interval-component",
            interval=60 * 1000,  # Actualisation every 60 seconde
            n_intervals=0,
        ),
        html.H2(children="Daily report"),
        dash_table.DataTable(
            id="daily-report-table",
            columns=[
                {"name": "Date", "id": "date"},
                {"name": "Open", "id": "open_price"},
                {"name": "Close", "id": "close_price"},
                {"name": "High", "id": "high_price"},
                {"name": "Low", "id": "low_price"},
                {"name": "Daily_Variation", "id": "Variation"},
                {"name": "Volatility", "id": "volatility"},
            ],
            style_cell={"textAlign": "center"},
            style_header={"backgroundColor": "rgb(211, 211, 211)", "fontWeight": "bold"},
        ),
    ]
)

@app.callback(
    Output("live-update-graph", "figure"),
    Input("interval-component", "n_intervals"),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
)

def update_dashboard(n, start_date, end_date):
    data = load_data()
    data = data[(data['timestamp'].dt.date >= pd.to_datetime(start_date)) & (data['timestamp'].dt.date <= pd.to_datetime(end_date))]
    
    trace = go.Scatter(x=data["timestamp"], y=data["price"], mode="lines+markers", name="price")

    return {
        "data": [trace],
        "layout": go.Layout(
            xaxis={"title": "Date"},
            yaxis={"title": "Price"},
            showlegend=True,
            margin=dict(l=40, r=0, t=40, b=30),   
     ),
  
    }
@app.callback(
    Output("daily-report-table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_daily_report(n):
    data = load_data()
    daily_data = daily_report(data)
    return daily_data.reset_index().to_dict("records")

if __name__ == "__main__":
    app.run_server(debug=True,host='0.0.0.0', port=8050 )
