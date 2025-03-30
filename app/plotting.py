import os
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.graph_objects as go
import streamlit as st

# Function to plot the discharge hydrograph using matplotlib
def plot_discharge_hydrograph(raw_data, site_no, USGS_data):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(raw_data.index, raw_data['discharge_cfs'], label="Discharge", color='green')
    ax.set_title(f"Discharge Hydrograph of {site_no}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Discharge (cfs)")
    ax.legend(loc='best', edgecolor='k')
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(USGS_data, f"Discharge_{site_no}.jpeg"))
    plt.close(fig)

# Function to plot a storm hydrograph using Plotly
def plot_hydrograph(storm_hydrograph):
    storm_hydrograph = storm_hydrograph.reset_index()
    storm_hydrograph['hover_text'] = (
        storm_hydrograph.index.astype(str) + ': ' +
        storm_hydrograph['datetimeUTC'].dt.strftime('%Y-%m-%d %H:%M:%S')
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=storm_hydrograph['datetimeUTC'],
        y=storm_hydrograph['discharge_cfs'],
        mode='lines',
        name='Discharge',
        text=storm_hydrograph['hover_text'],
        hoverinfo='text+y'
    ))

    fig.update_layout(
        xaxis=dict(title='Date and Time', showgrid=True),
        yaxis=dict(title='Discharge (cfs)'),
        title='Storm Hydrograph'
    )

    st.plotly_chart(fig)
