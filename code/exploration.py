import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
    # this avoids a warning when using the replace command
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
pio.templates.default = "seaborn"
import statsmodels.formula.api as sm
from scipy.stats import gaussian_kde
#from sklearn.linear_model import LinearRegression

# Create dataframe for first map-chart
def dataframe_map(df):

    df_map = df.drop(['Intra-EU Trade', 'Intra-Euro Trade'],axis=1).round(1)#.groupby(
                   # ['Country Code','Industry Code','Trade Country Code','Year']).sum().reset_index()

    # Add full names for countries and industries (previously only codes):
    df_map = pd.merge(df_map,pd.read_excel('../assets/codes.xlsx',sheet_name='Industries'),on='Industry Code')
    df_map = pd.merge(df_map,pd.read_excel('../assets/codes.xlsx',sheet_name='Countries'),on='Country Code')
    df_map = pd.merge(df_map,pd.read_excel('../assets/codes.xlsx',sheet_name='Countries').rename(
                    columns={'Country Code':'Trade Country Code','Country':'Trade Country'}),on='Trade Country Code')

    # Delete sales in own country (not relevant for figure):
    df_map = df_map[df_map['Country'] != df_map['Trade Country']]

    return df_map[df_map['Trade Country Code'] != 'ROW']

# Create summary statistics for all industries
def q25(x):
    return x.quantile(0.25)
def q75(x):
    return x.quantile(0.75)
def coef_var(x):
    return x.std() / x.mean()

def summary_table(df,var,year):
    df_statistics = (df[df['Year']==year][['Industry Code','Country Code','Year',var]].
    groupby(['Year','Industry Code','Country Code']).sum().reset_index().groupby(['Year','Industry Code']).agg(
            Mean_Sales=(var, 'mean'),
            Q25_Sales=(var, q25),
            Median_Sales=(var, 'median'),
            Q75_Sales=(var, q75),
            Variance_Coefficient_Sales=(var, coef_var)
    ))
    df_statistics = pd.merge(pd.read_excel('../assets/codes.xlsx',sheet_name='Industries'),df_statistics,on='Industry Code').drop('Industry Code',axis=1)
    for c in df_statistics.columns[1:5]:
        df_statistics[c] = df_statistics[c] / 1000
        df_statistics[c] = df_statistics[c].round(0).astype(int)
    df_statistics['Variance_Coefficient_Sales'] = df_statistics['Variance_Coefficient_Sales'].round(1)
    return df_statistics.set_index(['Industry']).sort_values('Mean_Sales',ascending=False)
