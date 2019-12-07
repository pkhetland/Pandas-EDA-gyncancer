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
from dataframes import unit_agg as uagg

external_stylesheets = [
    dbc.themes.BOOTSTRAP
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Gyncancer data EDA'

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>{%title%}</title>
        <link href="/assets/_favicon.png" rel="icon" type="image/x-icon">
        {%css%}
    </head>
    <body>
        <header class="container">
    </header>
        <div></div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div></div>
    </body>
</html>
'''


PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

server = app.server

dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Activity by division", href="#activity_by_division", external_link=True),
                dbc.DropdownMenuItem("Treatment time by division", href="#boxplot", external_link=True),
                dbc.DropdownMenuItem("Activities by unit", href="#activities_by_unit", external_link=True),
            ],
            nav=True,
            in_navbar=False,
            label="All graphs",
            direction='left',
            className="ml-auto flex-nowrap"
)


navbar = dbc.Navbar([
        # dbc.Row(
        #     [
        #         dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
        #         dbc.Col(dbc.NavbarBrand("EDA - INN350 Team 15", className="ml-3")),
        #     ],
        #     align="center",
        #     no_gutters=False,
        #     className='mr-0'
        # ),
        # dbc.DropdownMenu(
        #     children=[
        #         dbc.DropdownMenuItem("More pages", header=True),
        #         dbc.DropdownMenuItem("Activity by division", href="#activity_by_division", external_link=True),
        #         dbc.DropdownMenuItem("Treatment time by division", href="#boxplot", external_link=True),
        #         dbc.DropdownMenuItem("Activities by unit", href="#activities_by_unit", external_link=True),
        #     ],
        #     nav=True,
        #     in_navbar=False,
        #     label="All graphs",
        #     direction='left',
        #     className="ml-auto flex-nowrap"
        # )
    ],
    # color='dark',
    # dark=True,
    # className='ml-0 mr-0'
)

""" LAYOUT
"""

app.layout = dbc.Container(
    [
        dbc.Navbar([
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("EDA - INN350 Team 15", className="ml-3")),
                ],
                align="center",
                no_gutters=False,
                #className='mr-0'
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Activity by division", href="#activity_by_division", external_link=True),
                    dbc.DropdownMenuItem("Treatment time by division", href="#boxplot", external_link=True),
                    dbc.DropdownMenuItem("Activities by unit", href="#activities_by_unit", external_link=True),
                ],
                nav=True,
                in_navbar=False,
                label="All graphs",
                direction='left',
                className="ml-auto flex-nowrap"
            )
        ],
            color='dark',
            dark=True
        ),
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
                            width=12,
                            className="mt-5",
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
                            className="mt-5",
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
                            width=12,
                            className="mt-5",
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
                            className="mt-2 mb-5",
                            width=12,
                        ),
                    ],
                    width=6,
                ),
            ],
            align="start",
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
                    className="mt-5",
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
                    className="mb-5 mt-2",
                    width=11,
                ),
            ],
            align="start",
            justify="around",
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
                    className="mt-5",
                    id='boxplot',
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
            align="start",
            justify="center",
            className="mt-4"
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown(
                            "#### Histogram showing the distribution of total activities by `org.unit.name`",
                            style={"text-align": "center"},
                        )
                    ],
                    width=8,
                    className="mt-5",
                    id='activities_by_unit',
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            figure=(
                                px.histogram(
                                    uagg.iloc[0:10],
                                    x='unit_name',
                                    y='median_activities',
                                    histfunc='avg',
                                    color_discrete_sequence=['indianred'],
                                    opacity=0.7,
                                    log_y=True,
                                    labels={'unit_name': 'Unit/team name',
                                            'median_activities': 'activity count (log scale)'}

                                )
                            )
                        )
                    ],
                    className="mt-5 mb-5",
                    width=8,
                ),
            ],
            align="start",
            justify="center",
            className="mt-4"
        )
    ],
    fluid=True,
    style={'width': '100%'}
)

if __name__ == "__main__":
    app.run_server(debug=True)