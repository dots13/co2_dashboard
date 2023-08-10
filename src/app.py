
from dash import Dash, dcc, html, Input, Output
from dash import jupyter_dash
import os
import plotly.graph_objects as go
import pickle
import pandas as pd
import numpy as np

jupyter_dash.default_mode = "external"


# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [

    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = Dash(prevent_initial_callbacks="initial_duplicate",
           external_scripts=external_scripts,
           external_stylesheets=external_stylesheets,
           title="test_app")

server = app.server

# Path to data
script_dir = os.path.dirname(__file__)  # the cwd relative path of the script file
rel_path = "data/owid-world-data.csv"  # the target file
rel_to_cwd_path = os.path.join(script_dir, rel_path)  # the cwd-relative path of the target file

# Read csv file
df = pd.read_csv(rel_to_cwd_path)


# Path to model
rel_path_model = "models/model_co2.pkl"  # the target file
rel_to_cwd_path_model = os.path.join(script_dir, rel_path_model)  # the cwd-relative path of the target file

# Load model
loaded = pickle.load(open(rel_to_cwd_path_model, "rb"))

colors = {'background': '#111111',
          'text': '#7FDBFF'}

previous_co2 = df[df.year > 2000][['year', 'co2']]


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1("CO2 emissions forecast", 
            style={'display': 'block',
                   'margin-left': 'auto',
                   'margin-right': 'auto', 
                   'color': 'pink',
                   'text-align': 'center'}),
    ### control section
    html.Div([
        html.Div([
        dcc.Slider(1, 10, marks={i: f'{i}' for i in range(1, 10)}, value=5,
            id='slider',
            step=None,
            )],
            className="four columns",
            style={'width' : '50%',
                  'display': 'block',
                  'margin-left': 'auto',
                  'margin-right': 'auto'}),
        ],
        className="row" ,  
    ),    
    ### chart section
    html.Div([
        html.Div([
        dcc.Graph(id='chart1'),
        ],
        className="eight columns",
        style={'width' : '50%',
               'display': 'block',
               'margin-left': 'auto',
               'margin-right': 'auto'},),
    ],
    className="row"),
])

@app.callback(
    Output(component_id='chart1', component_property='figure', allow_duplicate=True),
    Input(component_id='slider', component_property='value'),
)
def generate_chart(value):
    forecast = loaded.forecast(value)
    forecast = np.insert(forecast, 0, previous_co2.co2.values[-1])
    year_list = [i for i in range(2021, 2022 + value)]
    

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=year_list, y=forecast, mode='lines+markers', name='forecast'))

    fig.add_trace(go.Scatter(x=previous_co2.year, y=previous_co2.co2, mode='lines+markers', name='previous'))
    fig.update_layout(
        autosize=True,
        height=500,
    #margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="black",
        template = 'plotly_dark+presentation'
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
