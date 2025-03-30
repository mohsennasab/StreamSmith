import os
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import streamlit as st

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

def DetectAndSavePeaks(discharge_filtered, prominence_value, USGS_data, site_no):
    peaks_info = plot_hydrographs_with_peaks(discharge_filtered, prominence_value, USGS_data, site_no)
    all_peaks_df = pd.concat(peaks_info)
    all_peaks_df.to_csv(os.path.join(USGS_data, f"Peaks_{site_no}_All_Years.csv"), index=False)
    return discharge_filtered['discharge_cfs'].std()

def update_peaks_data(peaks_file, indices_to_keep):
    try:
        st.write("Updating Peaks Data...")
        selected_indices = [int(idx.strip()) for idx in indices_to_keep.split(',')]
        peaks_df = pd.read_csv(peaks_file)
        updated_df = peaks_df[peaks_df['Index'].isin(selected_indices)]
        updated_df.to_csv(peaks_file, index=False)
        st.success("Peaks data updated successfully. Check the updated file.")
        st.write("Updated file saved to:", peaks_file)
    except ValueError as e:
        st.error(f"Invalid input for indices. Please enter comma-separated integers: {e}")
    except Exception as e:
        st.error(f"An error occurred while updating the file: {e}")
