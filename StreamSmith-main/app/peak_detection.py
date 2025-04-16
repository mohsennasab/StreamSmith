import os
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import streamlit as st
from .helpers import log_progress
from datetime import timedelta
from .plotting import plot_discharge_hydrograph_with_filtered_peaks



def plot_hydrographs_with_peaks(data, prominence_value, USGS_data, site_no):
    years = data.index.year.unique()
    first_legend_added = False
    peaks_info = []

    for year in years:
        yearly_data = data.loc[data.index.year == year].dropna(subset=['discharge_cfs'])
        peaks, _ = find_peaks(yearly_data['discharge_cfs'], prominence=prominence_value)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(yearly_data.index, yearly_data['discharge_cfs'], label=f"Discharge {year}", color='blue')
        ax.plot(yearly_data.index[peaks], yearly_data['discharge_cfs'].iloc[peaks], 'ro',
                label='Peak' if not first_legend_added else "")

        if not first_legend_added:
            ax.legend(loc='best', edgecolor='k')
            first_legend_added = True

        ax.set_title(f"Discharge Hydrograph with Peaks for {year}")
        ax.set_xlabel("Date")
        ax.set_ylabel('Discharge (cfs)')
        ax.xaxis.set_major_formatter(DateFormatter("%b %d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(USGS_data, f"Discharge_{site_no}_Hydrograph_with_Peaks_{year}.png"))
        plt.close(fig)

        peak_dates = yearly_data.index[peaks]
        peaks_df = pd.DataFrame({
            'Peak_Date': peak_dates,
            'Discharge_cfs': yearly_data['discharge_cfs'].iloc[peaks],
            'Index': peaks
        })

        peaks_info.append(peaks_df)

    return peaks_info

def DetectAndSavePeaks(discharge_filtered, prominence_value, USGS_data, site_no, min_peak_gap_hours):
    log_progress(USGS_data, f"Starting peak detection for site {site_no} with prominence value {prominence_value}")
    log_progress(USGS_data, f"Discharge stats — min: {discharge_filtered['discharge_cfs'].min()}, max: {discharge_filtered['discharge_cfs'].max()}, mean: {discharge_filtered['discharge_cfs'].mean()}")

    # First detect peaks
    peaks_info = []
    for year, group in discharge_filtered.groupby(discharge_filtered.index.year):
        peak_indices, _ = find_peaks(group['discharge_cfs'], prominence=prominence_value)
        year_peaks = group.iloc[peak_indices].copy()
        year_peaks["Index"] = peak_indices
        year_peaks["Year"] = year
        year_peaks["Peak_Date"] = group.iloc[peak_indices].index  # ✅ This line fixes the error
        peaks_info.append(year_peaks)


    all_peaks_df = pd.concat(peaks_info)


    # Log how many raw peaks were found
    log_progress(USGS_data, f"Initial peak detection found {len(all_peaks_df)} peaks for site {site_no}")

    # Convert Peak_Date to datetime (if not already)
    all_peaks_df['Peak_Date'] = pd.to_datetime(all_peaks_df['Peak_Date'])

    # Sort peaks by time
    all_peaks_df = all_peaks_df.sort_values(by='Peak_Date').reset_index(drop=True)

       
    # Initialize filtered list
    filtered_peaks = []
    last_kept_time = None
    last_kept_value = None


    # Loop through peaks and apply time + discharge similarity filter
    for _, row in all_peaks_df.iterrows():
        current_time = row['Peak_Date']
        current_value = row['discharge_cfs']  # ✅ Correct column name


        if last_kept_time is None:
            filtered_peaks.append(row)
            last_kept_time = current_time
            last_kept_value = current_value
            continue

        time_diff = current_time - last_kept_time
        value_diff = abs(current_value - last_kept_value) / max(last_kept_value, 1e-6)

        if time_diff >= timedelta(hours=min_peak_gap_hours) and value_diff > 0.01:
            filtered_peaks.append(row)
            last_kept_time = current_time
            last_kept_value = current_value

    # Convert list back to DataFrame
    filtered_df = pd.DataFrame(filtered_peaks)
    filtered_csv_path = os.path.join(USGS_data, f"Peaks_{site_no}_All_Years.csv")

    # Save the filtered peaks to CSV
    if not filtered_df.empty:
        filtered_df.to_csv(filtered_csv_path, index=False)
        log_progress(USGS_data, f"Saved final filtered peaks CSV to {filtered_csv_path}")
    else:
        log_progress(USGS_data, f"No peaks to save for site {site_no}. Skipping CSV export.")

    # Plot the hydrograph with filtered peaks
    plot_discharge_hydrograph_with_filtered_peaks(discharge_filtered, filtered_df, site_no, USGS_data)

    # Log results
    removed_count = len(all_peaks_df) - len(filtered_df)
    log_progress(USGS_data, f"Filtered {removed_count} similar/nearby peaks using min time gap of {min_peak_gap_hours} hours and 1% discharge threshold")
    log_progress(USGS_data, f"Saved final filtered peaks CSV to {filtered_csv_path}")

    return filtered_df

def update_peaks_data(peaks_file, indices_to_keep):
    try:
        st.write("Updating Peaks Data...")
        selected_indices = [int(idx.strip()) for idx in indices_to_keep.split(',')]
        peaks_df = pd.read_csv(peaks_file)
        updated_df = peaks_df[peaks_df['Index'].isin(selected_indices)]
        updated_df.to_csv(peaks_file, index=False)
        st.success("Peaks data updated successfully. Check the updated file.")
        st.write("Updated file saved to:", peaks_file)

        # Log the number of peaks kept
        log_progress(os.path.dirname(peaks_file), f"Updated peaks file with {len(updated_df)} peaks based on user input.")

    except ValueError as e:
        st.error(f"Invalid input for indices. Please enter comma-separated integers: {e}")
    except Exception as e:
        st.error(f"An error occurred while updating the file: {e}")


