import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import datetime
import plotly.express as px
import pandas as pd
import numpy as np


from dataframes import gyncancer_data as gdata
from dataframes import months_agg as magg
from dataframes import patient_agg as pagg

external_stylesheets = [
    dbc.themes.DARKLY
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Gyncancer data EDA'

server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("All graphs", header=True),
                dbc.DropdownMenuItem("Activity by division", href="#activity_by_division"),
                dbc.DropdownMenuItem("Treatment time by division", href="#boxplot"),
            ],
            nav=True,
            in_navbar=True,
            label="Choose graph",
        ),
    ],
    brand="NavbarSimple",
    brand_href="#",
    style={'width': '100%'}
)

""" LAYOUT
"""

app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Col(
                            [
                                dcc.Markdown(
                                    "#### `Activity` count over time per `division`, first 36 months",
                                    style={"text-align": "center"},
                                )
                            ],
                            width=11,
                            className="mt-5 mb-5",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure=(
                                        px.histogram(
                                            pagg,
                                            x="cancer_type",
                                            y="event_count",
                                            labels={
                                                "event_count": "patients",
                                                "cancer_type": "Cancer type",
                                            },
                                            histfunc="count",
                                            color_discrete_sequence=["indianred"],
                                            opacity=0.7
                                        )
                                    )
                                )
                            ],
                            className="mt-5 mb-5",
                            width=12,
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Col(
                            [
                                dcc.Markdown(
                                    "#### Histogram showing `average treatment time` by `cancer type`",
                                    style={"text-align": "center"},
                                )
                            ],
                            width=11,
                            className="mt-5 mb-5",
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure=(
                                        px.histogram(
                                            pagg,
                                            x="cancer_type",
                                            y="treatment_time_months",
                                            histfunc="avg",
                                            labels={
                                                "cancer_type": "Cancer type",
                                                "treatment_time_months": "treatment time (months)",
                                            },
                                        )
                                    )
                                )
                            ],
                            className="mt-5 mb-5",
                            width=12,
                        ),
                    ],
                    width=6,
                ),
            ],
            align="center",
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown(
                            "#### `Activity count` over time per `division`",
                            style={"text-align": "center"},
                        )
                    ],
                    className="mt-5 mb-5",
                    id='activity_by_division',
                    width=11,
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            figure=(
                                px.histogram(
                                    magg.loc[0:35],
                                    x="months_passed",
                                    y="activities_count",
                                    histfunc="sum",
                                    # histnorm='probability',
                                    color="division_name",
                                    nbins=47,
                                    marginal="box",
                                    opacity=0.8,
                                    labels={
                                        "activities_count": "unique activities",
                                        "months_passed": "Months passed since day 1",
                                    }
                                )
                            )
                        )
                    ],
                    className="mb-5 mt-5",
                    width=11,
                ),
            ],
            align="center",
            justify="center",
            className="mt-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown(
                            "#### Boxplot showing distribution of `treatment_time` by `cancer_type`",
                            style={"text-align": "center"},
                        )
                    ],
                    width=8,
                    id='boxplot',
                    className="mt-5 mb-5",
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            figure=(
                                px.box(
                                    pagg,
                                    x="cancer_type",
                                    y="treatment_time_months",
                                    points="all",
                                    labels={
                                        "treatment_time_months": "Treatment time in months",
                                        "cancer_type": "Cancer type",
                                    },
                                )
                            )
                        )
                    ],
                    className="mt-5 mb-5",
                    width=8,
                ),
            ],
            align="center",
            justify="center",
            className="mt-4",
        ),
    ],
    fluid=True,
    style={"width": "100%"}
)

if __name__ == "__main__":
    app.run_server(debug=True)