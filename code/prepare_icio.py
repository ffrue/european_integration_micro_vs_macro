"""
The functions in this file use the csv files containing the IO-table for one year (1995-2020)
and turn it into a dataframe with the necessary structure and labels for the analysis.
"""

import pandas as pd

def icio_to_dataframe(file):
    data = pd.read_csv(file)

    data.drop(data.filter(regex='T$|NPISH$|GGFC$|GFCF$|INVNT$|DPABR$').columns, axis=1, inplace=True)
        # drop columns on non-household final demand and households as employers (quantitatively irrelevant)
    data = data[~data['V1'].isin(['TLS','VA','OUT'])]
        # drop last three rows (taxes, value added, output)
    data[['Country Code','Industry Code']] = data['V1'].str.split(pat="_",n=1,expand=True)
    return data

def wide_to_long(data,var,year):
    df_source = data.melt(id_vars=['V1','Country Code','Industry Code'],
          var_name='Partner', value_name=var)
    df_source[['Trade Country Code','Trade Sector']] = df_source['Partner'].str.split(pat="_",n=1,expand=True)
    df_source.drop('Partner',axis=1,inplace=True)
    df_source['Year'] = year
    return df_source

def collapse_row(df_source,members):
    df_source.loc[~df_source['Country Code'].isin(members), 'Country Code'] = 'ROW'
    df_source.loc[~df_source['Trade Country Code'].isin(members), 'Trade Country Code'] = 'ROW'
        # sum up sales/imports for all non-eu countries
    df_source.loc[df_source['Industry Code'].str[0] != 'C', 'Industry Code'] = df_source[df_source['Industry Code'].str[0] != 'C']['Industry Code'].str[0]
        # aggregate all industry codes except C (manufacturing)
    return df_source.drop('V1', axis=1).groupby(
        ['Country Code', 'Industry Code', 'Trade Country Code', 'Trade Sector', 'Year'], as_index=False).sum()

def classify_trade(df_short,targets,var):
    df_short[var] = 0
    df_short.loc[(df_short['Country Code'].isin(targets)) &
                 (df_short['Trade Country Code'].isin(targets)) &
                 (df_short['Country Code'] != df_short['Trade Country Code']),var] = 1
    return df_short

# The data has the same shape for all years:
# for year in range(1995, 2020):
#     df = pd.read_csv(f'../data/icio/{year}_SML.csv')
#     print(f'The data in {year} has the shape {df.shape}')


# No longer needed:

#def transpose_icio_df(data):
#    data_length = len(data)
#    data_transpose = data[list(data.columns)[0:data_length]].copy()
#    data_transpose.loc[-1] = data_transpose.columns
#    data_transpose.index = data_transpose.index + 1
#    data_transpose = data_transpose.sort_index()
#        # make column names a standard row so that it1 gets transposed with the rest
#    data_transpose = data_transpose.transpose()
#    data_transpose.columns = data_transpose.iloc[0]
#    return data_transpose#[1:].reset_index(drop=True)'
