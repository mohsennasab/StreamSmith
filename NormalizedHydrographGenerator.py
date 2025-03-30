import streamlit as st
import pandas as pd
import os
import hydrofunctions as hf
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.express as px
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter1d
import numpy as np
from scipy.interpolate import interp1d

# The function updates the CSV file by keeping only the rows whose indices are specified in indices_to_keep.
def update_peaks_data(peaks_file, indices_to_keep):
    try:
        # Display a message indicating that the peaks data is being updated.
        st.write("Updating Peaks Data...")

        # Convert the string of indices into a list of integers.
        selected_indices = [int(idx.strip()) for idx in indices_to_keep.split(',')]

        # Load the peaks data from the CSV file into a pandas DataFrame.
        peaks_df = pd.read_csv(peaks_file)

        # Filter the DataFrame to keep only the rows with indices in selected_indices.
        updated_df = peaks_df[peaks_df['Index'].isin(selected_indices)]

        # Save the updated DataFrame back to the CSV file, without the index column.
        updated_df.to_csv(peaks_file, index=False)

        # Display a success message and the location of the updated file.
        st.success("Peaks data updated successfully. Check the updated file.")
        st.write("Updated file saved to:", peaks_file)  # Debugging information

    # Catch and handle ValueError if the indices_to_keep string is not properly formatted.
    except ValueError as e:
        st.error(f"Invalid input for indices. Please enter comma-separated integers: {e}")

    # Catch and handle any other exceptions that may occur during file operations.
    except Exception as e:
        st.error(f"An error occurred while updating the file: {e}")


# Function to create a folder at the given path if it does not exist
def CreateFolder(path):
    # Check if the folder at the given path does not exist
    if not os.path.exists(path):
        # If the folder does not exist, create it along with any necessary parent directories
        os.makedirs(path)

# Function to plot the discharge hydrograph
def plot_discharge_hydrograph(raw_data, site_no, USGS_data):
    # Create a figure and axis with specified size
    fig, ax = plt.subplots(figsize=(12,6))

    # Plot the discharge data on the axis
    ax.plot(raw_data.index, raw_data['discharge_cfs'], label="Discharge", color='green')

    # Setting the title of the plot using the site number
    ax.set_title(f"Discharge Hydrograph of {site_no}")

    # Setting the labels for x and y axes
    ax.set_xlabel("Date")
    ax.set_ylabel("Discharge (cfs)")

    # Adding a legend with a specified location and border color
    ax.legend(loc='best', edgecolor='k')

    # Formatting the x-axis to show dates in 'Month Year' format
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))

    # Rotating the date labels on the x-axis for better readability
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # Adjusting the layout to fit everything neatly
    plt.tight_layout()

    # Saving the figure as a JPEG file with a name based on the site number
    plt.savefig(USGS_data + "Discharge_" + site_no +".jpeg")

    # Closing the figure to free up memory
    plt.close(fig)

# Function to plot hydrographs with peaks for each year in the data
def plot_hydrographs_with_peaks(data, prominence_value, USGS_data, site_no):
    # Extract unique years from the data's index
    years = data.index.year.unique()

    # Flag to ensure the 'Peak' label is added only once in the legend
    first_legend_added = False

    # List to store information about peaks for each year
    peaks_info = []

    # Loop through each year to plot hydrographs
    for year in years:
        # Filter data for the current year and drop rows with missing discharge values
        yearly_data = data.loc[data.index.year == year].dropna(subset=['discharge_cfs'])

        # Find peaks in the discharge data with the specified prominence
        peaks, _ = find_peaks(yearly_data['discharge_cfs'], prominence=prominence_value)

        # Create a new figure and axis for plotting
        fig, ax = plt.subplots(figsize=(12,6))

        # Plot the discharge data for the year
        ax.plot(yearly_data.index, yearly_data['discharge_cfs'], label=f"Discharge {year}", color='blue')

        # Plot the peaks on the graph
        ax.plot(yearly_data.index[peaks], yearly_data['discharge_cfs'].iloc[peaks], 'ro', label='Peak' if not first_legend_added else "")

        # Add legend only for the first year's plot
        if not first_legend_added:
            ax.legend(loc='best', edgecolor='k')
            first_legend_added = True

        # Set the title, labels, and format the x-axis dates
        ax.set_title(f"Discharge Hydrograph with Peaks for {year}")
        ax.set_xlabel("Date")
        ax.set_ylabel('Discharge (cfs)')
        ax.xaxis.set_major_formatter(DateFormatter("%b %d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        plt.tight_layout()

        # Save the figure as a PNG file
        plt.savefig(USGS_data + f"Discharge_{site_no}_Hydrograph_with_Peaks_{year}.png")

        # Close the figure to free up memory
        plt.close(fig)

        # Record peak dates and discharge values in a DataFrame
        peak_dates = yearly_data.index[peaks]
        peaks_df = pd.DataFrame({
            'Peak_Date': peak_dates,
            'Discharge_cfs': yearly_data['discharge_cfs'].iloc[peaks],
            'Index': peaks
        })

        # Append the DataFrame to the list
        peaks_info.append(peaks_df)

    # Return the list of DataFrames containing peaks information for each year
    return peaks_info

# Function to retrieve and process flow data for a given site and date range
def GetFlow(site_no, begin_date, end_date, output_folder, user_months):
    # Retrieve discharge data using hydrofunctions
    discharge = hf.NWIS(site_no, 'iv', begin_date, end_date)

    # Prepare the folder path for saving data
    USGS_data = output_folder + '/USGS' + site_no + '/'
    
    # Create the folder if it does not exist
    CreateFolder(USGS_data)
    
    # Change the current directory to the USGS data folder
    os.chdir(USGS_data)

    # Extract discharge data and qualifiers from the retrieved data
    raw_data = pd.DataFrame({'discharge_cfs': discharge.df().iloc[:,0],
                             'qualifiers': discharge.df().iloc[:,1]})
    
    # Retrieve site information
    site_info = hf.site_file(site_no)
    site_info_df = pd.DataFrame(site_info.table)

    # Save the discharge data and site information to CSV files
    raw_data.to_csv(USGS_data + "USGS_Discharge_" + site_no + ".csv")
    site_info_df.to_csv(USGS_data + "site_" + site_no + "_info.csv")

    # Plot the discharge hydrograph
    plot_discharge_hydrograph(raw_data, site_no, USGS_data)

    # Reload the discharge data from the saved CSV file
    discharge_data = pd.read_csv(USGS_data + "USGS_Discharge_" + site_no + ".csv")
    discharge_data['datetimeUTC'] = pd.to_datetime(discharge_data['datetimeUTC'])
    discharge_data.set_index('datetimeUTC', inplace=True)

    # Filter the discharge data based on user-specified months
    return discharge_data[discharge_data.index.month.isin(user_months)], USGS_data


# Function to detect and save peak information in discharge data
def DetectAndSavePeaks(discharge_filtered, prominence_value, USGS_data, site_no):
    # Detect peaks in the filtered discharge data and plot hydrographs with peaks
    peaks_info = plot_hydrographs_with_peaks(discharge_filtered, prominence_value, USGS_data, site_no)

    # Combine peak information from all years into a single DataFrame
    all_peaks_df = pd.concat(peaks_info)

    # Save the combined peak information to a CSV file
    all_peaks_df.to_csv(USGS_data + f"Peaks_{site_no}_All_Years.csv", index=False)

    # Return the standard deviation of the filtered discharge data
    return discharge_filtered['discharge_cfs'].std()


# Function to read and process peaks and discharge data from CSV files
def read_data(peaks_file, discharge_file):
    # Read peaks data from the CSV file into a pandas DataFrame
    peaks_df = pd.read_csv(peaks_file)

    # Read discharge data from the CSV file into a pandas DataFrame
    discharge_data = pd.read_csv(discharge_file)

    # Convert the 'datetimeUTC' column to pandas datetime objects
    discharge_data['datetimeUTC'] = pd.to_datetime(discharge_data['datetimeUTC'])

    # Set 'datetimeUTC' as the index of the DataFrame
    discharge_data.set_index('datetimeUTC', inplace=True)

    # Return both DataFrames
    return peaks_df, discharge_data

# Function to plot a storm hydrograph using plotly
def plot_hydrograph(storm_hydrograph):
    # Reset the index to make 'datetimeUTC' a column and create a custom hover text column
    storm_hydrograph = storm_hydrograph.reset_index()
    storm_hydrograph['hover_text'] = storm_hydrograph.index.astype(str) + ': ' + storm_hydrograph['datetimeUTC'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Create an empty figure object
    fig = go.Figure()

    # Add a line trace for discharge with custom hover text
    fig.add_trace(go.Scatter(
        x=storm_hydrograph['datetimeUTC'], 
        y=storm_hydrograph['discharge_cfs'], 
        mode='lines', 
        name='Discharge',
        text=storm_hydrograph['hover_text'],
        hoverinfo='text+y'
    ))

    # Configure the layout of the plot
    fig.update_layout(
        xaxis=dict(title='Date and Time', showgrid=True),
        yaxis=dict(title='Discharge (cfs)'),
        title='Storm Hydrograph'
    )

    # Display the figure in a Streamlit application
    st.plotly_chart(fig)


# Function to get a subset of discharge data around a specified peak date
def get_storm_hydrograph(discharge_data, peak_date, window_size_before, window_size_after):
    # Check if the peak date is in the index of the discharge data
    if peak_date in discharge_data.index:
        # Get the index location of the peak date
        peak_idx = discharge_data.index.get_loc(peak_date)
    else:
        # If the peak date is not found, print a message and return None
        print(f"Peak date {peak_date} not found in discharge data.")
        return None

    # Calculate the start index for the window, ensuring it's not less than 0
    start = max(peak_idx - window_size_before, 0)

    # Calculate the end index for the window, ensuring it's not more than the length of the data
    end = min(peak_idx + window_size_after, len(discharge_data))

    # Return the subset of the data within the specified window
    return discharge_data.iloc[start:end]


# Function to process peak events and plot hydrographs in a Streamlit application
def process_peaks(peaks_df, discharge_data):
    # Initialize session state for storing events if not already present
    if 'events' not in st.session_state:
        st.session_state['events'] = {}

    # Iterate over each event in the peaks DataFrame
    for event_no, row in enumerate(peaks_df.itertuples(), start=1):
        # Initialize session state for the individual event if not already present
        event_key = f'event_{event_no}'
        if event_key not in st.session_state['events']:
            st.session_state['events'][event_key] = {'processed': False, 'window_before': 200, 'window_after': 200}

        # Convert peak date to pandas datetime
        peak_date = pd.to_datetime(row.Peak_Date)
        st.markdown(f"### Event {event_no}")

        # Create sliders for selecting window size before and after the peak
        window_before = st.slider(f"Window size before the peak for Event {event_no}", min_value=0, max_value=2000, value=st.session_state['events'][event_key]['window_before'], key=f'window_before_{event_no}')
        window_after = st.slider(f"Window size after the peak for Event {event_no}", min_value=0, max_value=2000, value=st.session_state['events'][event_key]['window_after'], key=f'window_after_{event_no}')

        # Create a button to process the event
        if st.button(f"Process Event {event_no}", key=f'process_{event_no}'):
            st.session_state['events'][event_key] = {'processed': True, 'window_before': window_before, 'window_after': window_after}

        # If the event is marked as processed, plot the hydrograph
        if st.session_state['events'][event_key]['processed']:
            storm_hydrograph = get_storm_hydrograph(discharge_data, peak_date, window_before, window_after)
            if storm_hydrograph is not None:
                plot_hydrograph(storm_hydrograph)

                # Create a button to save the hydrograph data to CSV
            if st.button("Save this hydrograph", key=f'save_{event_no}'):
                # Determine the year for naming the file, default to "unknown_year" if year is not available
                year = storm_hydrograph.index[0].year if not pd.isnull(storm_hydrograph.index[0]) else "unknown_year"
                
                # Save the storm hydrograph data to a CSV file
                storm_hydrograph.to_csv(f"Event_{event_no}_{year}.csv")
                
                # Display a success message upon saving the file
                st.success(f"Event {event_no} saved.")


# Function to calculate the Nash-Sutcliffe Efficiency
def nash_sutcliffe_efficiency(observed, simulated):
    """
    Calculate the Nash-Sutcliffe Efficiency coefficient.
    
    Parameters:
    observed (array-like): An array of observed data.
    simulated (array-like): An array of simulated or modelled data, corresponding to the observed data.

    Returns:
    float: The Nash-Sutcliffe Efficiency coefficient.
    """
    
    # Calculate the numerator of the NSE formula: the sum of the squared differences between observed and simulated values
    numerator = sum((simulated - observed) ** 2)

    # Calculate the denominator of the NSE formula: the sum of the squared differences between observed values and their mean
    denominator = sum((observed - np.mean(observed)) ** 2)

    # Calculate the NSE coefficient
    nse = 1 - (numerator / denominator)

    return nse

# Function to apply Gaussian smoothing to event data and analyze it
def apply_gaussian_smoothing(event_data, sigma):
    try:
        # Check if the 'discharge_cfs' column is present in the event data
        if 'discharge_cfs' not in event_data:
            st.error("Missing 'discharge_cfs' in data.")
            return None, None, None

        # Extract the discharge data
        discharge = event_data['discharge_cfs']

        # Apply Gaussian smoothing to the discharge data
        smoothed = gaussian_filter1d(discharge, sigma=sigma)

        # Creating a Plotly figure for visualization
        fig = go.Figure()

        # Add traces for original and smoothed discharge data
        fig.add_trace(go.Scatter(x=event_data['datetimeUTC'], y=discharge,
                                 mode='lines', name='Original Data'))
        fig.add_trace(go.Scatter(x=event_data['datetimeUTC'], y=smoothed,
                                 mode='lines', name=f'Smoothed with sigma={sigma}', line=dict(color='red')))

        # Update layout of the figure
        fig.update_layout(
            title="Original and Smoothed Hydrograph",
            xaxis_title="Date",
            yaxis_title="Discharge (cfs)",
            legend_title="Legend",
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="RebeccaPurple"
            )
        )

        # Display the figure in Streamlit
        st.plotly_chart(fig)

        # Calculate Nash-Sutcliffe Efficiency and peak difference
        nse = nash_sutcliffe_efficiency(discharge, smoothed)
        peak_diff = abs(np.max(discharge) - np.max(smoothed))

        # Add smoothed discharge data to the DataFrame
        event_data['smoothed_discharge_cfs'] = smoothed

        # Return the updated DataFrame, NSE, and peak difference
        return event_data, nse, peak_diff

    # Handle exceptions that occur during processing
    except Exception as e:
        st.error(f"An error occurred during Gaussian smoothing: {e}")
        return None, None, None
    

# Function to create a dimensionless unit hydrograph from smoothed data
def create_dimensionless_unit_hydrograph(smoothed_data):
    try:
        # Convert 'datetimeUTC' from string to datetime object and calculate the time in minutes since the start of the data
        smoothed_data['datetimeUTC'] = pd.to_datetime(smoothed_data['datetimeUTC'])
        smoothed_data['minutes'] = (smoothed_data['datetimeUTC'] - smoothed_data['datetimeUTC'].iloc[0]).dt.total_seconds() / 60

        # Check if the 'smoothed_discharge_cfs' column is present in the data
        if 'smoothed_discharge_cfs' not in smoothed_data:
            st.error("Missing 'smoothed_discharge_cfs' in data.")
            return pd.Series(), pd.Series()  # Return empty Series in case of error

        # Calculate base flow and generate the storm hydrograph
        base_flow = smoothed_data['smoothed_discharge_cfs'].iloc[0]
        storm_hydrograph = smoothed_data['smoothed_discharge_cfs'] - base_flow
        storm_hydrograph[storm_hydrograph < 0] = 0  # Set negative values to zero

        # Normalize the hydrograph to create a dimensionless unit hydrograph
        peak_discharge = storm_hydrograph.max()
        time_to_peak = smoothed_data['minutes'][storm_hydrograph.idxmax()]
        normalized_discharge = storm_hydrograph / peak_discharge
        normalized_time = smoothed_data['minutes'] / time_to_peak

        # Return the normalized discharge and time
        return normalized_discharge, normalized_time

    # Handle exceptions that occur during processing
    except Exception as e:
        st.error(f"An error occurred while creating dimensionless unit hydrograph: {e}")
        return pd.Series(), pd.Series()  # Return empty Series in case of error

# Function to process smoothed files and generate an overall DUH
def process_smoothed_files(directory):
    # Define a common time axis for interpolation
    common_time_axis = np.arange(0, 10.001, 0.001)  # Time axis from 0 to 10 with step 0.001
    all_interpolated_duhs = []

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        # Check if the file is a DUH event file
        if filename.startswith("DUH_Event_") and filename.endswith(".csv"):
            st.write(f"Processing {filename}...")

            # Read the DUH data from the file
            duh = pd.read_csv(os.path.join(directory, filename))

            # Interpolate the DUH data to the common time axis
            interpolated_values = interpolate_duh(duh, common_time_axis)
            if interpolated_values is not None and not interpolated_values.empty:
                # Convert interpolated values to a numpy array
                interpolated_array = interpolated_values['Normalized Discharge'].to_numpy()

                # Pad the array if it's shorter than the common time axis
                if len(interpolated_array) < len(common_time_axis):
                    interpolated_array = np.pad(interpolated_array, (0, len(common_time_axis) - len(interpolated_array)), 'constant', constant_values=np.nan)

                # Add the interpolated array to the list
                all_interpolated_duhs.append(interpolated_array)
            else:
                st.write(f"Warning: Could not interpolate {filename}")

    # Check if any valid DUH_Event files were processed
    if not all_interpolated_duhs:
        st.write("No valid DUH_Event files found or processed.")
        return pd.DataFrame(), []  # Return empty DataFrame and list

    # Calculate the overall DUH by averaging the interpolated DUHs
    overall_duh = np.nanmean(np.array(all_interpolated_duhs), axis=0)
    overall_duh_df = pd.DataFrame({'Normalized Time': common_time_axis, 'Normalized Discharge': overall_duh})

    # Return the overall DUH DataFrame and the list of interpolated DUHs
    return overall_duh_df, all_interpolated_duhs

# Function to interpolate a single DUH to a common time axis
def interpolate_duh(duh, common_time_axis, method='akima'):
    """
    Interpolates a single DUH to a common time axis using various interpolation methods.
    Supported methods include 'linear', 'quadratic', 'nearest', 'spline', 'polynomial', and 'akima'.

    Parameters:
    duh (DataFrame): The DUH data to be interpolated.
    common_time_axis (array-like): The common time axis to interpolate the data to.
    method (str): The method of interpolation to use.

    Returns:
    DataFrame: Interpolated DUH data.
    """

    # Setting 'Normalized Time' as the index for interpolation
    duh = duh.set_index('Normalized Time')

    # Handling interpolation based on the specified method
    # Special handling for 'spline' and 'polynomial' due to the need to specify an 'order'
    if method == 'spline' or method == 'polynomial':
        interpolated_duh = duh.reindex(common_time_axis).interpolate(method=method, order=3)  # 'order' can be changed for different curve fitting degrees
    else:
        # For other methods like 'linear', 'quadratic', 'nearest', 'akima'
        interpolated_duh = duh.reindex(common_time_axis).interpolate(method=method)

    # Resetting the index to convert 'Normalized Time' back to a column
    return interpolated_duh.reset_index()

# Function to plot multiple DUHs and the overall DUH
def plot_duhs(overall_duh_df, all_interpolated_duhs, common_time_axis, output_folder):
    # Create an empty Plotly figure
    fig = go.Figure()

    # Add a trace for each individual DUH in the list
    for index, duh in enumerate(all_interpolated_duhs):
        fig.add_trace(go.Scatter(x=common_time_axis, y=duh, mode='lines', name=f'Event DUH {index+1}', opacity=0.5))

    # Check if overall DUH DataFrame is provided and plot it
    if overall_duh_df is not None:
        fig.add_trace(go.Scatter(
            x=overall_duh_df['Normalized Time'], 
            y=overall_duh_df['Normalized Discharge'], 
            mode='lines', 
            name='Overall DUH', 
            line=dict(color='red', width=2)
        ))

        # Save the overall DUH data to a CSV file
        output_path = os.path.join(output_folder, "overall_duh.csv")
        try:
            overall_duh_df.to_csv(output_path, index=False)
            st.success(f"Overall DUH data saved successfully to {output_path}")
        except Exception as e:
            st.error(f"An error occurred while saving the file: {e}")

    # Update the layout of the figure
    fig.update_layout(
        title='Overall and Event Dimensionless Unit Hydrographs',
        xaxis_title='Normalized Time',
        yaxis_title='Normalized Discharge',
        legend_title="Legend"
    )

    # Display the figure in a Streamlit application
    st.plotly_chart(fig)



# Streamlit app main function
def main():
    st.title("Download Streamflow from USGS")
    st.write("""
             
             Developed by Mohsen Tahmasebi, PhD - https://www.hydromohsen.com/
             
             """)
    st.write("""Please note that this application helps you create normalized hydrographs. A normalized hydrograph is not 
             a standard unit hydrograph, as it lacks rainfall excess 
             information. A true unit hydrograph requires knowledge of 
             the effective rainfall that produced the observed runoff, 
             and the runoff volume would typically be normalized for both 
             the area of the watershed and the depth of the effective rainfall. 
             In the absence of effective rainfall data, this normalized hydrograph 
             provides a dimensionless representation of the discharge response, relative to the peak discharge.""")
    
    # Initialize session state variables

    # Step 1: Initial Setup - Gather Inputs
    site_no = st.text_input("Site Number", "05125039")
    begin_date = st.date_input("Begin Date", value=pd.to_datetime("2010-01-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2023-01-01"))
    output_folder = st.text_input("Output Folder")

    month_options = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
    selected_months = st.multiselect("Select Months for Peak Detection", month_options, default=["September", "October"])

    # Step 2: Call GetFlow - Button 1
    if st.button("Download Data"):
        if site_no and begin_date and end_date and output_folder and selected_months:
            months = [month_options.index(month) + 1 for month in selected_months]
            st.session_state.discharge_filtered, st.session_state.USGS_data = GetFlow(site_no, begin_date, end_date, output_folder, months)
            st.session_state.data_loaded = True

    # Conditional display of next steps based on the state of the data
    if st.session_state.get('data_loaded', False):
        # Step 3: User Input for Prominence Value and Detect Peaks - Button 2
        std_dev_suggestion = st.session_state.discharge_filtered['discharge_cfs'].std()
        prominence_value = st.number_input("Enter Prominence Value", value=std_dev_suggestion)
        if st.button("Detect and Save Peaks"):
            DetectAndSavePeaks(st.session_state.discharge_filtered, prominence_value, st.session_state.USGS_data, site_no)
            st.success("Peaks detected and saved successfully.")

        # Step 4: Display Peaks Data and Update Peaks - Button 3
        peaks_file_path = os.path.join(output_folder, f"USGS{site_no}", f"Peaks_{site_no}_All_Years.csv")
        if os.path.exists(peaks_file_path):
            peaks_df = pd.read_csv(peaks_file_path)
            st.write("Peaks Data:")
            st.dataframe(peaks_df)
            indices_to_keep = st.text_input("Enter the indices to keep (comma-separated, e.g., 500,705,2706):", key="indices_to_keep")
            if st.button("Update Peaks Data"):
                update_peaks_data(peaks_file_path, indices_to_keep)
                st.session_state.update_triggered = True

        # Step 5: Generate Hydrographs for Events - Button 4
        discharge_file_path = os.path.join(output_folder, f"USGS{site_no}", f"USGS_Discharge_{site_no}.csv")
        if st.session_state.get('update_triggered', False) and os.path.exists(discharge_file_path):
            st.title("Hydrograph Analysis Tool")
            if st.button("Start the Analysis"):
                st.session_state.start_analysis = True

        if st.session_state.get('start_analysis', False):
            peaks_df, discharge_data = read_data(peaks_file_path, discharge_file_path)
            process_peaks(peaks_df, discharge_data)

            # Processing Event files, Gaussian Smoothing - Button 5
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
                            st.success(f"Smoothed hydrograph saved as {smoothed_file}")

                            # Creating and Saving DUH_Event Files
                            normalized_discharge, normalized_time = create_dimensionless_unit_hydrograph(st.session_state.processed_event_data)
                            if not normalized_discharge.empty and not normalized_time.empty:
                                duh_df = pd.DataFrame({'Normalized Discharge': normalized_discharge, 'Normalized Time': normalized_time})
                                duh_file_name = f"DUH_Event_{event_no}.csv"
                                duh_df.to_csv(os.path.join(event_files_directory, duh_file_name), index=False)
                                st.write(f"DUH file created: {duh_file_name}")
                        except Exception as e:
                            st.error(f"An error occurred while saving the file: {e}")

            # Convert to Dimensionless Unit Hydrograph - Button 6
            if st.button("Convert to Normalized Hydrograph"):
                event_files_directory = os.path.join(output_folder, f"USGS{site_no}")
                if os.path.exists(event_files_directory):
                    try:
                        overall_duh_df, all_interpolated_duhs = process_smoothed_files(event_files_directory)
                        plot_duhs(overall_duh_df, all_interpolated_duhs, np.arange(0, 10.001, 0.001), output_folder)
                        st.success("Normalized Hydrographs processed and plotted successfully.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.error("Directory not found. Please check the output folder and site number.")

# Run the main function
if __name__ == "__main__":
    main()


    
    ## streamlit run NormalizedHydrographGenerator.py --server.port 8502

# df = pd.DataFrame(st.session_state['wordlist_unique'], columns=['words'])
# output_csv = df.to_csv(index=False).encode('utf-8')
# st.download_button('Download CSV', output_csv, file_name="vocabulary.csv", mime='text/csv')