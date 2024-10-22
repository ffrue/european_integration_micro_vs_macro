"""
This file contains different functions used in the analysis section
for modifying datasets and generating figures
"""

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

# Run regressions
def reg_stats(y_var,x_var,industry,df_ols):
    controls = df_ols.columns[7:]
    formula = f"{y_var} ~ {x_var} + " + " + ".join(controls)
        #
    mod = sm.ols(formula=formula,data=df_ols[df_ols['Industry']==industry])
    res = mod.fit()
    return pd.DataFrame({'Trade Type':[y_var.split('_')[0]], 'Join_Dummy':[x_var], 'Industry':[industry],
                         'Coefficient':[res.params[x_var]], 'p-Value':[res.pvalues[x_var]]})

def all_reg_stats(df_ols,significance=1):
    reg_results_stats = pd.DataFrame(columns=['Trade Type','Industry','Join_Dummy', 'Coefficient', 'p-Value'])
    for y_var in ['Exports_Ratio','Imports_Ratio']:
        for industry in pd.unique(df_ols['Industry']):
            for x_var in ['Five_Years_After', 'Ten_Years_After', 'EU_Member', 'Three_Years_Around']:
                try:
                    reg_results_stats = pd.concat([reg_results_stats, reg_stats(y_var,x_var,industry,df_ols)],ignore_index=True)
                except: # in case there is no variation for the JoinDummy in the industry sample
                    pass
    return reg_results_stats[reg_results_stats['p-Value']<significance].pivot(index=['Trade Type','Industry'], columns='Join_Dummy', values='Coefficient')

# Approximate histogram with Kernel-estimator
def histogram_estimator(data):
    fig = px.line(template='seaborn')

    # If data is a DataFrame with multiple columns, iterate over each column
    if isinstance(data, pd.DataFrame):
        for column in data.columns:
            column_data = data[column].dropna()
                # drop NaN values

            kde = gaussian_kde(column_data)
            x_vals = np.linspace(min(column_data), max(column_data), 1000)
                # define where kernel is evaluated
            kde_vals = kde(x_vals)

            fig.add_scatter(x=x_vals, y=kde_vals, mode='lines', name=column)

    # If data is a single array, treat it as a single dataset
    else:
        data = np.array(data).flatten()  # Ensure data is 1D
        kde = gaussian_kde(data)
        x_vals = np.linspace(min(data), max(data), 1000)
            # define where kernel is evaluated
        kde_vals = kde(x_vals)

        fig.add_scatter(x=x_vals, y=kde_vals, mode='lines', name='Data')

    fig.add_vline(x=0, line_width=3, line_color="black")
    fig.update_layout(xaxis_title="parameter estimates", yaxis_title="Density",
                      title="Distribution of single regressor coefficients")
    fig.update_legends(title="Regressor dummy")
    return fig

# Create summary heatmap
def estimates_heatmap(reg_results,type,zone):
    reg_results.loc[reg_results['Industry']=='All sectors','Industry'] = '<b>All sectors</b>'
    # hightlight all sectors 

    # Create color scale so that zero is always white, negative values are red, and positive values are green
    zero_percentile = abs(min(reg_results[reg_results['Trade Type']==type].min(numeric_only=True)))/(abs(min(reg_results[reg_results['Trade Type']==type].min(numeric_only=True))) + max(reg_results[reg_results['Trade Type']==type].max(numeric_only=True)))
    custom_color_scale = [
        [0, 'darkred'], 
        [zero_percentile/2, 'orange'],
        [zero_percentile, 'white'],
        [(1.5*zero_percentile), 'lightgreen'],
        [1, 'darkgreen']]
    
    fig = px.imshow((reg_results[reg_results['Trade Type']==type].round(2)[['Industry','Five_Years_After', 'Ten_Years_After', 'Three_Years_Around', f'{zone}_Member']]
              .set_index('Industry').sort_values(f'{zone}_Member',ascending=False)),
              aspect='auto',width=1000,height=800,color_continuous_scale=custom_color_scale,
              title=f'Effect of {zone} membership on relative <b>{type}</b> for different measures')
    fig.update_yaxes(title="")
    fig.update_xaxes(title="Regressor Dummy")
    return fig