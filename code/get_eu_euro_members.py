"""
This file builds a dataframe with yearly information of EU/Euro membership for different countries
by scraping the data from wikipedia. The above defined function are used to build a dataset
containing the membership status in EU/Eurozone for countries between 1995 and 2000
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
    # avoid warning when using replace-function in line 107

from bs4 import BeautifulSoup
import requests
from io import StringIO
import pycountry

import plotly.express as px
import plotly.io as pio
pio.templates.default = "seaborn"

# Two function to turn country codes into full names
def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        pass
def iso3_to_country(code):
    try:
        return pycountry.countries.get(alpha_3=code).name
    except AttributeError:
        pass

# Turn Wikipedia table into local dataframe
def table_to_df(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
        # parse the webpage using BeautifulSoup
    table = soup.find('table', {'class': 'wikitable'})
    html_string = str(table)
    df = pd.read_html(StringIO(html_string))[0]
        # convert table to dataframe
    df = df.rename(columns={df.columns[0]: 'Country', df.columns[1]: 'Country Code', df.columns[2]: 'Year'}
                     ).replace(r'\[.+\]', '', regex=True)[['Country','Country Code','Year']]
        # clean table of footnotes and rename columns
    df['Country Code'] = df['Country Code'].apply(iso2_to_iso3)
    return df

# Use previous function to either get EU or Euro entry years for all members
def get_wiki_table(zone):
    if zone == 'EU':
        # scrap info from wikipedia about EU:
        url_eu = "https://en.wikipedia.org/wiki/Member_state_of_the_European_Union"
        wiki_eu = table_to_df(url_eu)
        # manually add the UK (no longer in Wikipedia table):
        wiki_eu = pd.concat([wiki_eu, pd.DataFrame(
            {'Country': ['United Kingdom'], 'Country Code': ['GBR'], 'Year': ['1 January 1973']})], ignore_index=True)
        # adjust the table for own needs:
        wiki_eu.replace({'Founder': '1 January 1958'}, inplace=True)
        wiki_eu['Year'] = pd.to_numeric(wiki_eu['Year'].str[-4:])
        return wiki_eu

    elif zone == 'Euro':
        url_euro = "https://en.wikipedia.org/wiki/Eurozone"
        wiki_euro = table_to_df(url_euro).drop(20)
        # drop last row of wikipedia table (entry "eurozone")
        wiki_euro['Year'] = pd.to_numeric(wiki_euro['Year'])
        return wiki_euro
    else:
        print('Only works for EU or Eurozone')

# Change format of previous dataframe so that we have a country's membership for each year
def country_year_dataframe(df_info,cat_var):
    countries = pd.unique(df_info['Country Code'])
    years = list(range(min(pd.unique(df_info['Year'])), 2021))

    cut_off_info = df_info.set_index('Country Code')['Year'].to_dict()
        # creates dictionary with year of accession per country

    country_year_pairs = pd.MultiIndex.from_product(
        [countries, years],
        names=['Country Code', 'Year']
    ).to_frame(index=False)

    df_target = pd.merge(df_info, country_year_pairs, how='outer')
    df_target[cat_var] = 'No'

    for c in pd.unique(df_target['Country Code']):
        df_target.loc[(df_target['Country Code'] == c) & (df_target['Year'] >= cut_off_info[c]), cat_var] = 'Yes'
    df_target.loc[(df_target['Country Code'] == 'GBR') & (df_target['Year']==2020), cat_var] = 'No'
    return df_target

# Combine the previous functions and run them together
def build_membership_df():

    df_eu = country_year_dataframe(get_wiki_table('EU'), 'EU')
    df_euro = country_year_dataframe(get_wiki_table('Euro'), 'Euro')

    # Combine data and return dataframe:

    df =  pd.merge(df_eu, df_euro.drop('Country', axis=1), on=['Year', 'Country Code'], how='left').fillna(
        'No')
    df['Country'] = df['Country Code'].apply(iso3_to_country)
    return df

# Generate membership bar graph
def eu_euro_members(df_membership):
    fig = px.bar(df_membership.replace(to_replace=['Yes', 'No'], value=[1, 0]).groupby(['Year']).agg(
        EU=('EU', 'sum'),
        Eurozone=('Euro', 'sum')).reset_index(),
                 x='Year', y=['EU', 'Eurozone'], barmode='group', color_discrete_sequence=['blue', 'orange'],
                 title='<b>Number of member states in EU and Eurozone over time</b><br><i style="font-size:13;">Dark area = Years in dataset</i>')
    fig.update_layout(margin=dict(l=100, r=100, t=80, b=60))
    fig.update_yaxes(title="")
    fig.update_legends(title="", orientation="h", yanchor="top", y=0.9, xanchor="left", x=0.1)
    fig.add_vrect(x0=1994.5, x1=2020.5, y0=0, y1=1, opacity=0.2)
    return fig