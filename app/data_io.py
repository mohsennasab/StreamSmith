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
    except HydroNoDataError:
        msg = f"No data available for site {site_no} between {begin_date} and {end_date}."
        st.error(msg)
        log_progress(USGS_data, msg)
        raise  # Let the app stop as before
  

    raw_data = pd.DataFrame({
        'discharge_cfs': discharge.df().iloc[:, 0],
        'qualifiers': discharge.df().iloc[:, 1]
    })

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
