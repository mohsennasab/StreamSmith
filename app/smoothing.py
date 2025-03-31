import os
import numpy as np
import pandas as pd
import streamlit as st
from scipy.ndimage import gaussian_filter1d
from plotly import graph_objects as go

def nash_sutcliffe_efficiency(observed, simulated):
    numerator = sum((simulated - observed) ** 2)
    denominator = sum((observed - np.mean(observed)) ** 2)
    return 1 - (numerator / denominator)

def apply_gaussian_smoothing(event_data, sigma):
    try:
        if 'discharge_cfs' not in event_data:
            st.error("Missing 'discharge_cfs' in data.")
            return None, None, None

        discharge = event_data['discharge_cfs']
        smoothed = gaussian_filter1d(discharge, sigma=sigma)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=event_data['datetimeUTC'], y=discharge, mode='lines', name='Original Data'))
        fig.add_trace(go.Scatter(x=event_data['datetimeUTC'], y=smoothed, mode='lines',
                                 name=f'Smoothed with sigma={sigma}', line=dict(color='red')))
        fig.update_layout(
            title="Original and Smoothed Hydrograph",
            xaxis_title="Date",
            yaxis_title="Discharge (cfs)",
            legend_title="Legend",
            font=dict(family="Courier New, monospace", size=12, color="RebeccaPurple")
        )
        st.plotly_chart(fig)

        nse = nash_sutcliffe_efficiency(discharge, smoothed)
        peak_diff = abs(np.max(discharge) - np.max(smoothed))

        event_data['smoothed_discharge_cfs'] = smoothed
        return event_data, nse, peak_diff

    except Exception as e:
        st.error(f"An error occurred during Gaussian smoothing: {e}")
        return None, None, None

def create_dimensionless_unit_hydrograph(smoothed_data):
    try:
        smoothed_data['datetimeUTC'] = pd.to_datetime(smoothed_data['datetimeUTC'])
        smoothed_data['minutes'] = (smoothed_data['datetimeUTC'] - smoothed_data['datetimeUTC'].iloc[0]).dt.total_seconds() / 60

        if 'smoothed_discharge_cfs' not in smoothed_data:
            st.error("Missing 'smoothed_discharge_cfs' in data.")
            return pd.Series(), pd.Series()

        base_flow = smoothed_data['smoothed_discharge_cfs'].iloc[0]
        storm_hydrograph = smoothed_data['smoothed_discharge_cfs'] - base_flow
        storm_hydrograph[storm_hydrograph < 0] = 0

        peak_discharge = storm_hydrograph.max()
        time_to_peak = smoothed_data['minutes'][storm_hydrograph.idxmax()]
        normalized_discharge = storm_hydrograph / peak_discharge
        normalized_time = smoothed_data['minutes'] / time_to_peak

        return normalized_discharge, normalized_time

    except Exception as e:
        st.error(f"An error occurred while creating dimensionless unit hydrograph: {e}")
        return pd.Series(), pd.Series()

def interpolate_duh(duh, common_time_axis, method='akima'):
    duh = duh.set_index('Normalized Time')
    if method in ['spline', 'polynomial']:
        interpolated_duh = duh.reindex(common_time_axis).interpolate(method=method, order=3)
    else:
        interpolated_duh = duh.reindex(common_time_axis).interpolate(method=method)
    return interpolated_duh.reset_index()

def process_smoothed_files(directory):
    common_time_axis = np.arange(0, 10.001, 0.001)
    all_interpolated_duhs = []

    for filename in os.listdir(directory):
        if filename.startswith("DUH_Event_") and filename.endswith(".csv"):
            st.write(f"Processing {filename}...")
            duh = pd.read_csv(os.path.join(directory, filename))
            interpolated_values = interpolate_duh(duh, common_time_axis)
            if interpolated_values is not None and not interpolated_values.empty:
                interpolated_array = interpolated_values['Normalized Discharge'].to_numpy()
                if len(interpolated_array) < len(common_time_axis):
                    interpolated_array = np.pad(interpolated_array, (0, len(common_time_axis) - len(interpolated_array)),
                                                'constant', constant_values=np.nan)
                all_interpolated_duhs.append(interpolated_array)
            else:
                st.write(f"Warning: Could not interpolate {filename}")

    if not all_interpolated_duhs:
        st.write("No valid DUH_Event files found or processed.")
        return pd.DataFrame(), []

    overall_duh = np.nanmean(np.array(all_interpolated_duhs), axis=0)
    overall_duh_df = pd.DataFrame({'Normalized Time': common_time_axis, 'Normalized Discharge': overall_duh})

    return overall_duh_df, all_interpolated_duhs

def plot_duhs(overall_duh_df, all_interpolated_duhs, common_time_axis, output_folder):
    fig = go.Figure()

    for index, duh in enumerate(all_interpolated_duhs):
        fig.add_trace(go.Scatter(x=common_time_axis, y=duh, mode='lines', name=f'Event DUH {index+1}', opacity=0.5))

    if overall_duh_df is not None:
        fig.add_trace(go.Scatter(
            x=overall_duh_df['Normalized Time'],
            y=overall_duh_df['Normalized Discharge'],
            mode='lines',
            name='Overall DUH',
            line=dict(color='red', width=2)
        ))

        # output_path = os.path.join(output_folder, f"USGS{site_no}", "overall_duh.csv")
        # try:
        #     overall_duh_df.to_csv(output_path, index=False)
        #     st.success(f"Overall DUH data saved successfully to {output_path}")
        # except Exception as e:
        #     st.error(f"An error occurred while saving the file: {e}")

    fig.update_layout(
        title='Overall and Event Dimensionless Unit Hydrographs',
        xaxis_title='Normalized Time',
        yaxis_title='Normalized Discharge',
        legend_title="Legend"
    )
    st.plotly_chart(fig)
