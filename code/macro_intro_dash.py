from dash import Dash, dcc, html, Input, Output
import pandas as pd
import datetime

import plotly.express as px
import plotly.io as pio
pio.templates.default = "seaborn"

macro_df = pd.read_csv('../temp/macro-data.csv')
macro_df_agg = macro_df.drop('Country', axis=1).groupby(['Country Group', 'Date']).mean().reset_index()
for ind in ['Inflation', 'Unemployment', 'Long-Term Interest Rate']:
    macro_df_agg[ind] = macro_df_agg[ind] / 100

# Initialize the Dash app
app_macro = Dash(__name__)

# Layout for the Dash App
app_macro.layout = html.Div([
    html.H1("Macro indicators for different country groups in Europe", style={'padding-left': '5%'}),

    # Dropdown for Indicator Selection
    html.Div([
        # html.Label("Select Indicator:"),
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': 'Inflation', 'value': 'Inflation'},
                     {'label': 'Unemployment', 'value': 'Unemployment'},
                     {'label': 'Long-Term Interest Rate', 'value': 'Long-Term Interest Rate'}],
            value='Inflation',  # Default value
            clearable=False
        )
    ], style={'width': '30%', 'padding-left': '5%', 'margin-bottom': '1%'}),

    # Graph with custom width
    dcc.Graph(
        id='line-chart',
        style={'width': '90%', 'margin': '0 auto'}
    )
], style={'backgroundColor': '#f0f0f0', 'padding': '20px'})


# Callback to update the graph based on selected indicator
@app_macro.callback(
    Output('line-chart', 'figure'),
    Input('indicator-dropdown', 'value')
)
def update_graph(indicator):

    # Plotly Express line chart
    fig = px.line(
        macro_df_agg.reset_index(),
        x='Date',
        y=indicator,
        color='Country Group',
        title=f'Development of {indicator}'
    )

    fig.add_vline(x=datetime.datetime(2004, 1, 1).timestamp() * 1000,
                  # there is a bug that does not allow to select a point on a date axis in a simpler way
                  annotation_text='Eastern enlargement ', line_width=3, line_color='orange',
                  annotation_position='top left', annotation_font={'color': 'orange', 'size': 14})
    fig.add_vline(x=datetime.datetime(2007, 1, 1).timestamp() * 1000,
                  # there is a bug that does not allow to select a point on a date axis in a simpler way
                  annotation_text=' First latecomers', line_width=3, line_color='green',
                  annotation_position='top right', annotation_font={'color': 'green', 'size': 14})

    fig.update_layout(margin=dict(l=50, r=50, t=80, b=60), yaxis_tickformat='0%')
    fig.update_yaxes(title="")
    fig.update_legends(title="", orientation="h", yanchor="top", y=1.1, xanchor="left", x=0.02)

    return fig