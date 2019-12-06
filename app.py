import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import datetime
import plotly.express as px
import pandas as pd
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

''' Defining main dataset and making early adjustments
'''
# Main dataset
gyncancer_data = pd.read_csv('gyncancer_data.csv')

# Early adjustments
gyncancer_data['event.timestamp'] = pd.to_datetime(gyncancer_data['event.timestamp'])

gyncancer_data = gyncancer_data.sort_values(['patient.id', 'event.timestamp'])

# Sorting out irrelevant data points
gyncancer_data = gyncancer_data[gyncancer_data['patient.diagnosis'] != 'No cancer diagnosed']

gyncancer_data = gyncancer_data[gyncancer_data['patient.diagnosis'] != 'Unspecified tumor']

# Generate columns with extra information
gyncancer_data['days_since_first_ts'] = (
    gyncancer_data
    .groupby('patient.id')
    .apply(
        lambda df: df['event.timestamp'] - df['event.timestamp'].min()
    )
    .reset_index(level=1)
    .set_index('level_1')
)

gyncancer_data['all_time_days_passed'] = gyncancer_data['event.timestamp'] - gyncancer_data['event.timestamp'].min()

gyncancer_data['month_per_patient'] = ((gyncancer_data['days_since_first_ts'])/np.timedelta64(1, 'M')).astype(int)

gyncancer_data['all_time_months_passed'] = ((gyncancer_data['all_time_days_passed'])/np.timedelta64(1, 'M')).astype(int)

gyncancer_data = gyncancer_data.sort_values(['all_time_months_passed'])

# Creating 'months_agg' dataframe
months_agg = gyncancer_data.groupby(['all_time_months_passed', 'org.division.name'])

months_agg = months_agg.agg(
    activities_count = ('event.timestamp', 'count'),
    average_age = ('patient.age', 'mean'),
    first_ts = ('event.timestamp', 'min'),
    last_ts = ('event.timestamp', 'max'),
    months_passed = ('all_time_months_passed', 'max'),
    division_name = ('org.division.name', 'first')
)

months_agg = months_agg.sort_values(['all_time_months_passed', 'activities_count'], ascending=True)


''' LAYOUT
'''

app.layout = dbc.Container(
    [dbc.Row([
        dbc.Col([
            html.H4('Activity count over time per division',
                style={'text-align': 'center'})
            ], width=8, className='mt-5 mb-5'),
        dbc.Col([
            dcc.Graph(figure=(
                px.histogram(
                    months_agg.loc[0:35],
                    x='months_passed',
                    y='activities_count',
                    histfunc='sum',
                    # histnorm='probability',
                    color='division_name',
                    nbins=47,
                    marginal='box',
                    opacity=0.8,
                    labels={'activities_count': 'unique activities', 'months_passed': 'Months passed since day 1'},
                    title='Unique activities by division over time:'
                )))
        ], width=8)
        ], align='center', justify='center')
    ])

if __name__ == '__main__':
    app.run_server(debug=True)