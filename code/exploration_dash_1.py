"""
Generates first dash application in section V
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
    # this avoids a warning when using the replace command
import pandas as pd

import plotly.express as px
import plotly.io as pio
pio.templates.default = "seaborn"

from dash import Dash, dcc, html, Input, Output, State

#---------------------------------------------------------------------------------------------------------------
# Create first Dash application

df_map = pd.read_csv('../temp/df_map.csv')
app_map = Dash(__name__)

# Layout of the dashboard
app_map.layout = html.Div([
    html.H1("European Export and Import Patterns over Time"),

    html.Div([
        # Dropdown for Industry selection
        dcc.Dropdown(
            id='industry-dropdown',
            options=[{'label': industry, 'value': industry} for industry in df_map['Industry'].unique()],
            value='Machinery and equipment',  # default option
            clearable=False,
            style={'width': '100%'}
        ),

        # Dropdown for selecting Exports or Imports
        dcc.Dropdown(
            id='trade-type-dropdown',
            options=[
                {'label': 'Sales Shares', 'value': 'Sales Shares'},
                {'label': 'Purchases Shares', 'value': 'Purchases Shares'}
            ],
            value='Sales Shares',  # default option
            clearable=False,
            style={'width':'100%'}
        ),

        # Display selected Country Code, styled like a dropdown
        html.Div(id='selected-country', style={
            'fontSize': 15,
            'width': '80%',
            'backgroundColor': 'white',
            'border': '1px solid black',
            'padding': '6px',
            'borderRadius': '5px',
            'align-items': 'center'
        }),

        # Button to start the animation
        html.Button('Animate', id='start-animation', n_clicks=0, style={'width':'15%','padding': '6px'}),

    ], style={'display': 'flex', 'padding-top':'20px', 'align-items': 'center'}),

    # Slider for selecting Year
    dcc.Slider(
        id='year-slider',
        min=1995,
        max=2020,
        step=1,
        value=1995,  # Default to the minimum year
        marks=dict(zip(range(1995, 2021), [str(i) for i in range(1995, 2021)]))
    ),

    # Hidden interval component to control the year animation
    dcc.Interval(
        id='year-interval',
        interval=500,  # Interval in milliseconds (1 second)
        n_intervals=0,   # Number of intervals passed
        disabled=True    # Initially disabled
    ),

    # Choropleth Map
    dcc.Graph(id='graph')

], style={'backgroundColor': '#f0f0f0', 'padding': '20px'})


# Callback to handle map updates based on the selected inputs and animation
@app_map.callback(
    [Output('graph', 'figure'),
     Output('selected-country', 'children')],
    [Input('industry-dropdown', 'value'),
     Input('trade-type-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('graph', 'clickData')]
)

def update_map(selected_industry, selected_trade_type, selected_year, click_data):
    # Default option
    selected_country_code = 'POL'
    # If a country is clicked, update the selected country code
    if click_data:
        selected_country_code = click_data['points'][0]['location']

    # Filter the DataFrame based on the selected Country Code, Industry, and Year
    filtered_df = df_map[
        (df_map['Country Code'] == selected_country_code) &
        (df_map['Industry'] == selected_industry) &
        (df_map['Year'] == selected_year)
    ]

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        fig = px.choropleth()  # Create an empty figure
        fig.add_annotation(text="No data available for the selected filters.",
                           xref="paper", yref="paper", showarrow=False, font=dict(size=20))
        selected_country_text = "No country selected"
    else:
        # Create choropleth map using the selected trade type (Exports or Imports)
        fig = px.choropleth(
            filtered_df,
            locations='Trade Country Code',  # Column with trade country codes
            locationmode='ISO-3',  # Use ISO-3 country codes for map matching
            color=selected_trade_type,  # Color countries by the selected trade type (Exports or Imports)
            hover_name='Trade Country Code',  # Hover info shows the Trade Country Code
            color_continuous_scale=px.colors.sequential.Plasma,
            range_color=[0,max(df_map[(df_map['Country Code'] == selected_country_code)&(df_map['Industry'] == selected_industry)][selected_trade_type])]
        )
        selected_country_text = f"Selected Country: {selected_country_code}"

    # Update layout for better map visualization, limit to Europe
    fig.update_coloraxes(
        colorbar=dict(
            ticksuffix=" %",  # add percentage signs
        )
    )
    
    fig.update_layout(
        geo=dict(
            showcoastlines=True,
            projection_type='natural earth',
            scope='europe'  # Limit the map to Europe
        ),
        margin={"r": 0, "t": 40, "l": 0, "b": 0}  # Adjust margins
    )

    return fig, selected_country_text


# Callback to handle year slider animation
@app_map.callback(
    Output('year-slider', 'value'),
    [Input('year-interval', 'n_intervals')],
    [State('year-slider', 'value')]
)

def update_year(n_intervals, current_year):
    # Update the year based on the interval (loop from 1995 to 2020)
    if current_year >= 2020:
        return 1995  # Reset to the minimum year
    else:
        return current_year + 1


# Callback to enable the interval (animation) when the button is clicked
@app_map.callback(
    Output('year-interval', 'disabled'),
    [Input('start-animation', 'n_clicks')],
    [State('year-interval', 'disabled')]
)

def toggle_animation(n_clicks, interval_disabled):
    # Start or stop the animation based on button clicks
    if n_clicks > 0:
        return not interval_disabled
    return interval_disabled