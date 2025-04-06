import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def seasonal_maintenances(df, region):
    """
    Creates a seasonal graph for maintenances.

    Args:
        df: The dataset with the refinery maintenance data extracted from the EA API

    Returns:
        The seasonal graph
    """
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    
    # Plotting
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Month', y=f'Monthly refinery total estimated impact in {region} in kb/d', hue='Year', marker='o')
    
    # Dashed lines for EA forecast for refinery unplanned outages
    plt.plot(df['Month'], df[f'Monthly EA forecast for refinery unplanned outages in {region} in kb/d'], linestyle='--', color='grey')
    
    plt.title(f'EA Refinery Outage Impact and Forecasted Unplanned Outages for {region}')
    plt.xticks(ticks=range(1, 13), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.xlabel('Month')
    plt.ylabel('kbbl/d')
    plt.legend(title='Year')
    plt.show()


def unit_maintenances(df, region):
    """
    Creates a bar graph showing the maintenances in a given region separated by unit.

    Args:
        df: The dataset with the refinery maintenance data extracted from the EA API

    Returns:
        The unit maintenance bar graph
    """

    # Reorder and rename df
    df = df[df.columns[[0,3,4,5,6]]]
    df = df.rename(columns={f'Monthly refinery total outages for CDU units in {region} in kb/d': 'CDU',
                            f'Monthly refinery total outages for FCC units in {region} in kb/d': 'FCC',
                            f'Monthly refinery total outages for HCU units in {region} in kb/d': 'HCU',
                            f'Monthly refinery total outages for COK units in {region} in kb/d': 'COK'})
    
    # Melt the dataframe for seaborn
    df_melted = df.melt(id_vars='Date', var_name='Category', value_name='Absolute Value')
    
    # Create a stacked graph
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_melted, x='Date', y='Absolute Value', hue='Category')
    plt.title(f'EA Monthly Outages by Unit in {region}')
    plt.xlabel('Date')
    plt.ylabel('kbbl/d')
    plt.legend(title='Unit')
    ticks = df_melted['Date'].unique()
    labels = [d.strftime('%b/%Y') for d in ticks]
    plt.xticks(ticks=range(len(ticks)), labels=labels, rotation=45)
    plt.tight_layout()
    plt.show()
    