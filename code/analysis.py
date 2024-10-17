"""
This file containts different functions used in the analysis section
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
#from sklearn.linear_model import LinearRegression

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
    # Create a figure object
    fig = px.line(template='seaborn')

    # If data is a DataFrame with multiple columns, iterate over each column
    if isinstance(data, pd.DataFrame):
        for column in data.columns:
            column_data = data[column].dropna()  # Drop NaN values (if any)

            # Create a Kernel Density Estimate (KDE) for each column
            kde = gaussian_kde(column_data)

            # Generate points where the KDE will be evaluated
            x_vals = np.linspace(min(column_data), max(column_data), 1000)
            kde_vals = kde(x_vals)

            # Add each KDE line to the plot with the column name as the label
            fig.add_scatter(x=x_vals, y=kde_vals, mode='lines', name=column)

    # If data is a single array, treat it as a single dataset
    else:
        data = np.array(data).flatten()  # Ensure data is 1D
        kde = gaussian_kde(data)

        # Generate points where the KDE will be evaluated
        x_vals = np.linspace(min(data), max(data), 1000)
        kde_vals = kde(x_vals)

        # Add the single KDE line to the plot
        fig.add_scatter(x=x_vals, y=kde_vals, mode='lines', name='Data')

    # Set labels and show the plot
    fig.add_vline(x=0, line_width=3, line_color="black")
    fig.update_layout(xaxis_title="parameter estimates", yaxis_title="Density",
                      title="Distribution of single regressor coefficients")
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
    
    return px.imshow((reg_results[reg_results['Trade Type']==type].round(2)[['Industry','Five_Years_After', 'Ten_Years_After', 'Three_Years_Around', f'{zone}_Member']]
              .set_index('Industry').sort_values(f'{zone}_Member',ascending=False)),
              aspect='auto',width=1000,height=800,color_continuous_scale=custom_color_scale,
              title=f'Effect of {zone} membership on relative <b>{type}</b> for different measures')

#----------------------------------------------------------------------------------------------------
# No longer used:

# Run single-regressor regressions
def single_effect(r,X,y):
    leave_out = ['Five_Years_After', 'Ten_Years_After', 'Three_Years_Around', 'EU_Member']
    leave_out.remove(r)
    reg = LinearRegression()
    reg.fit(X=X.drop(leave_out,axis=1),y=y)
    return round(reg.coef_[0],2)

# Run single-regressor regressions with all potential JoinDummies
def all_effects(var,industry,X,y):
    estimates = {'Trade Type':var}
    estimates['Industry'] = industry
    for r in ['Five_Years_After', 'Ten_Years_After', 'Three_Years_Around', 'EU_Member']:
        estimates[r] = single_effect(r,X,y)
    return pd.DataFrame([estimates])