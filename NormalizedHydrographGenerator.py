import streamlit as st
import pandas as pd
import os
import numpy as np


from app.data_io import GetFlow, read_data
from app.helpers import CreateFolder, log_progress
from app.plotting import plot_hydrograph
from app.peak_detection import DetectAndSavePeaks, update_peaks_data
from app.smoothing import (
    apply_gaussian_smoothing,
    create_dimensionless_unit_hydrograph,
    process_smoothed_files,
    plot_duhs
)

# Function to get a subset of discharge data around a specified peak date
def get_storm_hydrograph(discharge_data, peak_date, window_size_before, window_size_after):
    if peak_date in discharge_data.index:
        peak_idx = discharge_data.index.get_loc(peak_date)
    else:
        print(f"Peak date {peak_date} not found in discharge data.")
        return None

    start = max(peak_idx - window_size_before, 0)
    end = min(peak_idx + window_size_after, len(discharge_data))
    return discharge_data.iloc[start:end]

# Function to process peak events and plot hydrographs in a Streamlit application
def process_peaks(peaks_df, discharge_data):
    if 'events' not in st.session_state:
        st.session_state['events'] = {}

    for event_no, row in enumerate(peaks_df.itertuples(), start=1):
        event_key = f'event_{event_no}'
        if event_key not in st.session_state['events']:
            st.session_state['events'][event_key] = {'processed': False, 'window_before': 200, 'window_after': 200}

        peak_date = pd.to_datetime(row.Peak_Date)
        st.markdown(f"### Event {event_no}")

        window_before = st.slider(f"Window size before the peak for Event {event_no}",
                                  min_value=0, max_value=2000,
                                  value=st.session_state['events'][event_key]['window_before'],
                                  key=f'window_before_{event_no}')
        window_after = st.slider(f"Window size after the peak for Event {event_no}",
                                 min_value=0, max_value=2000,
                                 value=st.session_state['events'][event_key]['window_after'],
                                 key=f'window_after_{event_no}')

        if st.button(f"Process Event {event_no}", key=f'process_{event_no}'):
            st.session_state['events'][event_key] = {
                'processed': True,
                'window_before': window_before,
                'window_after': window_after
            }

        if st.session_state['events'][event_key]['processed']:
            storm_hydrograph = get_storm_hydrograph(discharge_data, peak_date, window_before, window_after)
            if storm_hydrograph is not None:
                plot_hydrograph(storm_hydrograph)

            if st.button("Save this hydrograph", key=f'save_{event_no}'):
                year = storm_hydrograph.index[0].year if not pd.isnull(storm_hydrograph.index[0]) else "unknown_year"
                save_dir = st.session_state.USGS_data  
                save_path = os.path.join(save_dir, f"Event_{event_no}_{year}.csv")
                log_progress(st.session_state.USGS_data, f"Saved Event {event_no} hydrograph to Event_{event_no}_{year}.csv")
                storm_hydrograph.to_csv(save_path)
                st.success(f"Event {event_no} saved to {save_path}.")



# Streamlit app main function
def main():
    st.title("StreamSmith: Find the highs, smooth the rest, and build the hydrograph.")
    st.write("""
        Developed by Mohsen Tahmasebi Nasab, PhD – https://www.hydromohsen.com/
    """)
    st.write("""
        💧 This application allows you to generate normalized unit hydrographs (NUHs) 
             Unlike traditional unit hydrographs, normalized hydrographs are based solely on 
             streamflow data and do not incorporate rainfall excess information. Instead, 
             they provide a standardized shape of the runoff response, ideal for visualizing 
             and comparing storm events across time and location.
             This application helps you create normalized unit hydrographs.
    """)

    site_no = st.text_input("USGS Site Number (https://dashboard.waterdata.usgs.gov/app/nwd/en/)", "05125039")
    begin_date = st.date_input("Begin Date", value=pd.to_datetime("2010-01-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2023-01-01"))
    output_folder = st.text_input("Output Folder")

    month_options = ["All"] + list(range(1, 13))
    selected_months = st.multiselect(
        "Select Months for Peak Detection",
        options=month_options,
        default="All"
    )

    # Convert "All" to full list of months
    if "All" in selected_months:
        months = list(range(1, 13))
    else:
        months = selected_months

    if st.button("Download Data"):
        if site_no and begin_date and end_date and output_folder and selected_months:
            st.session_state.discharge_filtered, st.session_state.USGS_data = GetFlow(site_no, begin_date, end_date, output_folder, months)
            st.session_state.data_loaded = True

    if st.session_state.get('data_loaded', False):
        std_dev_suggestion = st.session_state.discharge_filtered['discharge_cfs'].std()

        prominence_value = st.number_input("Enter Prominence Value", value=std_dev_suggestion)

        st.caption("""
        **ℹ️ What is prominence?**  
        Prominence controls how much a peak must stand out from surrounding data.  
        - **Lower values** will detect more small peaks (including noise)  
        - **Higher values** will detect only the most significant peaks

        A good starting point is the standard deviation of the discharge, as suggested.
        """)

        min_peak_gap = st.number_input("Minimum time between peaks (hours)", min_value=1, value=12)

        st.caption("""
        **ℹ️ What is minimum time between peaks?**  
        If multiple peaks occur within this number of hours and have nearly the same discharge, only one will be kept.  
        This helps avoid saving flat-topped hydrographs as separate storms.
        """)


        if st.button("Detect and Save Peaks"):
            if st.session_state.get('data_loaded', False):
                try:
                    # Run peak detection
                    st.session_state.peaks_df = DetectAndSavePeaks(
                        st.session_state.discharge_filtered,
                        prominence_value,
                        st.session_state.USGS_data,
                        site_no,
                        min_peak_gap
                    )
                except Exception as e:
                    st.error(f"An error occurred during peak detection: {e}")
                    log_progress(st.session_state.USGS_data, f"Error during peak detection: {e}")

        # Always try to retrieve the stored peaks_df from session state
        peaks_df = st.session_state.get('peaks_df', None)

        if peaks_df is not None and not peaks_df.empty:
            st.success("Peaks detected and saved successfully.")
            st.write("Peaks Data:")
            st.dataframe(peaks_df)

            peaks_file_path = os.path.join(output_folder, f"USGS{site_no}", f"Peaks_{site_no}_All_Years.csv")


            # Show input for indices only if peaks are available
            indices_to_keep = st.text_input("Enter the indices to keep (comma-separated, e.g., 500,705,2706):", key="indices_to_keep")
            if st.button("Update Peaks Data"):
                update_peaks_data(peaks_file_path, indices_to_keep)
                st.session_state.update_triggered = True

        elif "peaks_df" in st.session_state:
            st.warning("No peaks were detected for the selected site and parameters. Try lowering the prominence value.")



        discharge_file_path = os.path.join(output_folder, f"USGS{site_no}", f"USGS_Discharge_{site_no}.csv")
        if st.session_state.get('update_triggered', False) and os.path.exists(discharge_file_path):
            st.title("Hydrograph Analysis Tool")
            if st.button("Start the Analysis"):
                st.session_state.start_analysis = True

        if st.session_state.get('start_analysis', False):
            peaks_df, discharge_data = read_data(peaks_file_path, discharge_file_path)
            process_peaks(peaks_df, discharge_data)

            event_files_directory = os.path.join(output_folder, f"USGS{site_no}")
            if os.path.exists(event_files_directory):
                files_to_process = [f for f in os.listdir(event_files_directory) if f.startswith("Event_") and f.endswith(".csv")]
                selected_file = st.selectbox("Select a file to process", files_to_process)
                sigma_value = st.slider("Select Sigma Value for Gaussian Smoothing", min_value=0.0, max_value=100.0, value=10.0)

                if st.button("Apply Gaussian Smoothing"):
                    event_file = os.path.join(event_files_directory, selected_file)
                    event_data = pd.read_csv(event_file, parse_dates=['datetimeUTC'])
                    processed_data, nse, peak_diff = apply_gaussian_smoothing(event_data, sigma_value)
                    st.session_state.processed_event_data = processed_data
                    st.write(f"Nash-Sutcliffe Efficiency: {nse:.2f}")
                    st.write(f"Peak Difference: {peak_diff:.2f}")

                if 'processed_event_data' in st.session_state and st.session_state.processed_event_data is not None:
                    if st.button("Save Smoothed Data"):
                        try:
                            event_no = selected_file.split('_')[1].split('.')[0]
                            smoothed_file = os.path.join(event_files_directory, f"S_Event_{event_no}.csv")
                            st.session_state.processed_event_data.to_csv(smoothed_file, index=False)
                            log_progress(event_files_directory, f"Smoothed hydrograph saved as S_Event_{event_no}.csv")
                            st.success(f"Smoothed hydrograph saved as {smoothed_file}")

                            normalized_discharge, normalized_time = create_dimensionless_unit_hydrograph(st.session_state.processed_event_data)
                            if not normalized_discharge.empty and not normalized_time.empty:
                                duh_df = pd.DataFrame({'Normalized Discharge': normalized_discharge, 'Normalized Time': normalized_time})
                                duh_file_name = f"DUH_Event_{event_no}.csv"
                                duh_df.to_csv(os.path.join(event_files_directory, duh_file_name), index=False)
                                log_progress(event_files_directory, f"DUH file created: DUH_Event_{event_no}.csv")
                                st.write(f"DUH file created: {duh_file_name}")
                        except Exception as e:
                            st.error(f"An error occurred while saving the file: {e}")

            if st.button("Convert to Normalized Hydrograph"):
                event_files_directory = os.path.join(output_folder, f"USGS{site_no}")
                if os.path.exists(event_files_directory):
                    try:
                        overall_duh_df, all_interpolated_duhs = process_smoothed_files(event_files_directory)
                        
                        # ✅ Save the overall DUH before plotting
                        output_path = os.path.join(event_files_directory, "overall_duh.csv")
                        overall_duh_df.to_csv(output_path, index=False)
                        log_progress(event_files_directory, "Saved overall normalized hydrograph to overall_duh.csv")

                        # ✅ Plot the DUH
                        plot_duhs(overall_duh_df, all_interpolated_duhs, np.arange(0, 10.001, 0.001), output_folder)

                        log_progress(event_files_directory, "Normalized Hydrographs processed and plotted successfully.")
                        st.success("Normalized Hydrographs processed and plotted successfully.")

                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        log_progress(event_files_directory, f"Error while processing DUHs: {e}")

                else:
                    st.error("Directory not found. Please check the output folder and site number.")

if __name__ == "__main__":
    main()
