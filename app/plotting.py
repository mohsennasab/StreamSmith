import os
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.graph_objects as go
import streamlit as st
from .helpers import log_progress


# Function to plot the discharge hydrograph using matplotlib
def plot_discharge_hydrograph(raw_data, site_no, USGS_data):
    # Log data summary
    log_progress(USGS_data, f"Discharge data summary:\n{raw_data['discharge_cfs'].describe()}")

    # Drop rows with missing discharge values
    raw_data = raw_data.dropna(subset=['discharge_cfs'])

    # Prevent plotting if the data is empty
    if raw_data.empty:
        log_progress(USGS_data, "No valid discharge data to plot. Skipping hydrograph.")
        return

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




def plot_discharge_hydrograph_with_filtered_peaks(discharge_df, filtered_peaks, site_no, folder):
    discharge_df = discharge_df.copy()
    filtered_peaks = filtered_peaks.copy()

    # 🛡️ Check for empty or missing columns
    if filtered_peaks.empty or 'Peak_Date' not in filtered_peaks.columns:
        return

    # Extract years from filtered peaks
    filtered_peaks['Year'] = filtered_peaks['Peak_Date'].dt.year
    unique_years = filtered_peaks['Year'].unique()

    for year in unique_years:
        # Filter data for the current year
        year_discharge = discharge_df[discharge_df.index.year == year]
        year_peaks = filtered_peaks[filtered_peaks['Year'] == year]

        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(year_discharge.index, year_discharge['discharge_cfs'], 'b-', label='Discharge')
        ax.plot(year_peaks['Peak_Date'], year_peaks['discharge_cfs'], 'ro', label='Filtered Peaks')

        ax.set_title(f"Discharge Hydrograph with Filtered Peaks for {year}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Discharge (cfs)")
        ax.legend()
        ax.xaxis.set_major_formatter(DateFormatter("%b %d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        plt.tight_layout()

        # Save the figure
        output_path = os.path.join(folder, f"Discharge_{site_no}_Hydrograph_with_Filtered_Peaks_{year}.png")
        plt.savefig(output_path)
        plt.close()

