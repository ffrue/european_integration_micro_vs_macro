import pandas as pd
import numpy as np
import eurostat
import pycountry

import plotly.express as px
import plotly.io as pio
pio.templates.default = "seaborn"

def iso2_to_country(code):
    # used in following function
    try:
        return pycountry.countries.get(alpha_2=code).name
    except AttributeError:
        pass

def get_macro_data():
    # Download inflation data
    df = eurostat.get_data_df('prc_hicp_manr')
    inflation = df[df['coicop'] == 'CP00'].drop(['freq','unit','coicop'],axis=1).rename(columns={r'geo\TIME_PERIOD':'Country ISO2'})
    inflation = inflation.set_index('Country ISO2').stack().reset_index().rename(columns={'level_1':'Date',0:'Inflation'})

    # Download unemployment data
    df = eurostat.get_data_df('ei_lmhr_m')
    unemployment = df[(df['indic']=='LM-UN-T-TOT')&(df['s_adj']=='NSA')].drop(['freq','unit','s_adj','indic'],axis=1).rename(columns={r'geo\TIME_PERIOD':'Country ISO2'})
    unemployment = unemployment.set_index('Country ISO2').stack().reset_index().rename(columns={'level_1':'Date',0:'Unemployment'})

    # Download interest rate data
    df = eurostat.get_data_df('irt_lt_mcby_m').drop(['freq','int_rt'],axis=1).rename(columns={r'geo\TIME_PERIOD':'Country ISO2'})
    interest = df.set_index('Country ISO2').stack().reset_index().rename(columns={'level_1':'Date',0:'Long-Term Interest Rate'})

    # Merge all indicators together
    macro_df = pd.merge(pd.merge(inflation,unemployment,on=['Country ISO2','Date']),interest,on=['Country ISO2','Date'])

    # Turn Date into datetime
    macro_df['Date'] = pd.to_datetime(macro_df['Date'], format="%Y-%m")

    # Add country names
    macro_df['Country'] = macro_df['Country ISO2'].apply(iso2_to_country)
    macro_df = macro_df[~macro_df['Country'].isna()]
        # drop non-countries (e.g. aggregate EU data)
    macro_df.drop('Country ISO2', axis=1, inplace=True)

    return macro_df


def dispersion_graph(macro_df):
    # Use variance as crude dispersion measure
    dispersion = macro_df.drop(['Country'], axis=1).groupby('Date').var().apply(np.sqrt).round(2)

    fig = px.line(dispersion.reset_index(), x='Date', y=['Inflation', 'Unemployment', 'Long-Term Interest Rate'],
            title="<b>Variance of macro indicators across Europe</b>")
    fig.update_layout(margin=dict(l=50, r=50, t=80, b=60))
    fig.update_xaxes(title="")
    fig.update_yaxes(title="cross-country variance")
    fig.update_legends(title="")#, orientation="h", yanchor="top", y=1.1, xanchor="left", x=0.29)

    return fig