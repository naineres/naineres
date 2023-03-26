
import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
import pandas as pd

# Define the URL of the webpage containing the price
url = 'https://www.blockchainevent.fr/crypto/matic-polygon/'

# Send a GET request to the webpage and extract the HTML content
response = requests.get(url)
html_content = response.text

# Extract the price from the HTML content using regex (similar to the grep command)
import re
matches = re.findall(r'<span class="cryptowp-text-price-amount">([0-9\.]+)</span>', html_content)
prices = [float(match) for match in matches]

# Convert the list of prices to a Pandas DataFrame with a datetime index
timestamps = pd.date_range(start=pd.Timestamp.now(), periods=len(prices), freq='s')
df = pd.DataFrame({'Price': prices}, index=timestamps)


# Define a function to compute the daily report
def compute_daily_report(df):
    daily_report = {}

    # Compute the daily volatility
    #df['Price'] = pd.to_numeric(df['Price'].str.replace(',', ''), errors='coerce')
    daily_report['Volatility'] = df['Price'].pct_change().std() * (252 ** 0.5)


    # Compute the open and close prices
    daily_report['Open'] = df.iloc[0]['Price']
    daily_report['Close'] = df.iloc[-1]['Price']

    # Compute the evolution
    daily_report['Evolution'] = (daily_report['Close'] - daily_report['Open']) / daily_report['Open']

    return daily_report

# Compute the daily report using the entire DataFrame
daily_report = compute_daily_report(df)


# Create the Dash app
app = dash.Dash()

# Define the layout of the dashboard
app.layout = html.Div(children=[
    html.H1(children='Matic Price Dashboard'),
    html.Div(children=f'The current Matic price is {prices}'),
    dcc.Graph(
        id='price-graph',
        figure={
            'data': [
                {'x': df.index, 'y': df['Price'], 'type': 'line', 'name': 'Price'},
            ],
            'layout': {
                'title': 'Matic Price evolution'
            }
        }
    ),
    html.H2(children='Daily Report'),
    html.Table(
        children=[
            html.Tr(
                children=[
                    html.Th('Metric'),
                    html.Th('Value')
                ]
            ),
            html.Tr(
                children=[
                    html.Td('Volatility'),
                    html.Td(f'{daily_report["Volatility"]:.2%}')
                ]
            ),
            html.Tr(
                children=[
                    html.Td('Open'),
                    html.Td(f'{daily_report["Open"]:.2f}')
                ]
            ),
            html.Tr(
                children=[
                    html.Td('Close'),
                    html.Td(f'{daily_report["Close"]:.2f}')
                ]
            ),
            html.Tr(
                children=[
                    html.Td('Evolution'),
                    html.Td(f'{daily_report["Evolution"]:.2%}')
                ]
            ),
        ]
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug = False, host='0.0.0.0', port=8050)
