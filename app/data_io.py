# Directory: app/data_io.py

import os
import pandas as pd
import hydrofunctions as hf
from hydrofunctions.exceptions import HydroNoDataError
from .helpers import CreateFolder
from .plotting import plot_discharge_hydrograph
from .helpers import CreateFolder, log_progress
import streamlit as st




def GetFlow(site_no, begin_date, end_date, output_folder, user_months):
    USGS_data = os.path.join(output_folder, f'USGS{site_no}')
    CreateFolder(USGS_data)

    try:
        discharge = hf.NWIS(site_no, 'iv', begin_date, end_date)
        log_progress(USGS_data, f"Raw NWIS columns: {discharge.df().columns.tolist()}")

    except HydroNoDataError:
        msg = f"No data available for site {site_no} between {begin_date} and {end_date}."
        st.error(msg)
        log_progress(USGS_data, msg)
        raise  # Let the app stop as before


    # Get the actual discharge column (parameter 00060)
    # Identify available columns
    columns = discharge.df().columns.tolist()
    log_progress(USGS_data, f"Raw NWIS columns: {columns}")

    # Safely extract the discharge columns (parameter 00060 = streamflow)
    discharge_cols = [col for col in columns if ':00060:' in col and 'qualifiers' not in col]
    qualifier_cols = [col for col in columns if ':00060:' in col and 'qualifiers' in col]

    # If not found, notify user and stop
    if not discharge_cols or not qualifier_cols:
        msg = (
            f"No streamflow data (parameter 00060) found for site {site_no}. "
            f"Available columns: {columns}"
        )
        st.error(msg)
        log_progress(USGS_data, msg)
        raise ValueError(msg)

    # Use the first matching column
    discharge_column = discharge_cols[0]
    qualifier_column = qualifier_cols[0]
    log_progress(USGS_data, f"Using discharge column: {discharge_column}")


    raw_data = pd.DataFrame({
        'discharge_cfs': discharge.df()[discharge_column],
        'qualifiers': discharge.df()[qualifier_column]
    })


    # Filter out rows with "hf.upsampled" or "hf.missing" qualifiers (Added 05/13/2025)
    raw_data = raw_data[~raw_data['qualifiers'].isin(['hf.upsampled', 'hf.missing'])]


    log_progress(USGS_data, f"Started data download for site {site_no}")

    site_info = hf.site_file(site_no)
    site_info_df = pd.DataFrame(site_info.table)

    raw_data.to_csv(os.path.join(USGS_data, f"USGS_Discharge_{site_no}.csv"))

    log_progress(USGS_data, f"Saved discharge CSV for site {site_no}")

    site_info_df.to_csv(os.path.join(USGS_data, f"site_{site_no}_info.csv"))

    log_progress(USGS_data, f"Saved site info CSV for site {site_no}")

    plot_discharge_hydrograph(raw_data, site_no, USGS_data)

    discharge_data = pd.read_csv(os.path.join(USGS_data, f"USGS_Discharge_{site_no}.csv"))
    discharge_data['datetimeUTC'] = pd.to_datetime(discharge_data['datetimeUTC'])
    discharge_data.set_index('datetimeUTC', inplace=True)

    return discharge_data[discharge_data.index.month.isin(user_months)], USGS_data

def read_data(peaks_file, discharge_file):
    peaks_df = pd.read_csv(peaks_file)
    discharge_data = pd.read_csv(discharge_file)
    discharge_data['datetimeUTC'] = pd.to_datetime(discharge_data['datetimeUTC'])
    discharge_data.set_index('datetimeUTC', inplace=True)
    return peaks_df, discharge_data
