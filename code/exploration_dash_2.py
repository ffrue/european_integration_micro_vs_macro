"""
Generates second dash application in section V
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
    # this avoids a warning when using the replace command
import pandas as pd

import plotly.express as px
import plotly.io as pio
pio.templates.default = "seaborn"
from dash import Dash, dcc, html, Input, Output, State

from get_eu_euro_members import *
df_analysis = pd.read_csv('../temp/df_analysis.csv')
eu_join = get_wiki_table('EU')
eu_join_year = dict(zip(eu_join['Country'], eu_join['Year']))

# Initialize the Dash app inside Jupyter
app_timeline = Dash(__name__)

# Layout for the Dash App
app_timeline.layout = html.Div([
    html.H1("Change in Relative Trade with other EU Members"),

    # Div for placing selectors side by side
    html.Div([
        # Dropdown for Sector Selection
        html.Div([
            html.Label("Select Sector:"),
            dcc.Dropdown(
                id='sector-dropdown',
                options=[{'label': sector, 'value': sector} for sector in df_analysis['Industry'].unique()],
                value=df_analysis['Industry'].unique()[0],  # Default value
                clearable=False
            )
        ], style={'width': '40%', 'display': 'inline-block'}),  # Set width and inline-block

        # Dropdown for Country Selection
        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in df_analysis['Country'].unique()],
                value='Poland',  # Default value
                clearable=False
            )
        ], style={'width': '20%', 'display': 'inline-block', 'marginLeft': '2%'})  # Adjust margin for spacing
    ], style={'marginBottom': '30px'}),

    # Graph with custom width
    dcc.Graph(
        id='line-chart',
        style={'width': '90%', 'margin': '0 auto'}
    )
], style={'backgroundColor': '#f0f0f0', 'padding': '20px'})


# Callback to update the graph based on selected sector and country
@app_timeline.callback(
    Output('line-chart', 'figure'),
    [Input('sector-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_graph(selected_sector, selected_country):
    # Filter DataFrame based on selected sector and country
    filtered_df = df_analysis[(df_analysis['Industry'] == selected_sector) & (df_analysis['Country'] == selected_country)]

    # Plotly Express line chart
    fig = px.line(
        filtered_df,
        x='Year',
        y=['Exports in/out EU', 'Imports in/out EU'],
        title=f'Trade patterns for {selected_sector.lower()} in {selected_country}',
    )

    # Keep axis range more stable:
    fig.update_yaxes(range=[0, 1.2 * max([max(pd.unique(df_analysis.loc[(df_analysis['Country'] == selected_country) & (
                df_analysis['Industry'] == selected_sector), 'Exports in/out EU'])),
                                          max(pd.unique(df_analysis.loc[(df_analysis['Country'] == selected_country) & (
                                                      df_analysis['Industry'] == selected_sector), 'Imports in/out EU']))])])

    fig.update_layout(margin=dict(l=50, r=50, t=80, b=60))
    fig.update_yaxes(title="")
    fig.update_legends(title="", orientation="h", yanchor="top", y=1.1, xanchor="left", x=0.02)

    if selected_country in eu_join_year.keys():
        if eu_join_year[selected_country] < 1995:
            fig.add_vrect(x0=1995, x1=2020,
                          annotation_text="EU Membership", annotation_position="top",
                          fillcolor="green", opacity=0.10, line_width=0,
                          annotation=dict(font_size=15, font_color="green"))
        else:
            fig.add_vrect(x0=eu_join_year[selected_country], x1=2020,
                          annotation_text="EU Membership", annotation_position="top",
                          fillcolor="green", opacity=0.10, line_width=0,
                          annotation=dict(font_size=15, font_color="green"))

    return fig