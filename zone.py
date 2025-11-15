import streamlit as st
import pandas as pd
from datetime import datetime

# Configure the page
st.set_page_config(page_title="Driver-Pincode Summary", layout="wide")
st.title("🚚 Driver-Pincode Monthly Summary")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Convert date columns to datetime
        df['Scheduled At'] = pd.to_datetime(df['Scheduled At'], format='%d-%b-%Y', errors='coerce')
        
        # Debug: Show available dates
        st.sidebar.write("Debug Info:")
        st.sidebar.write(f"Total records: {len(df)}")
        st.sidebar.write(f"Date range: {df['Scheduled At'].min()} to {df['Scheduled At'].max()}")
        
        # Define the delivery hubs we're interested in
        target_hubs = [
            'Banashankari [ BH Micro warehouse ]',
            'Chandra Layout [ BH Micro warehouse ]', 
            'Domlur [ BH Micro warehouse ]',
            'Hebbal [ BH Micro warehouse ]',
            'Kudlu [ BH Micro warehouse ]',
            'Mahadevapura [ BH Micro warehouse ]'
        ]
        
        # Filter data for target hubs
        df_filtered = df[df['Delivery Hub'].isin(target_hubs)].copy()
        
        if df_filtered.empty:
            st.warning("No data found for the specified delivery hubs.")
        else:
            # Create filters
            st.sidebar.header("Filters")
            
            # Extract available months from data and filter for Sep, Oct, Nov only
            df_filtered['Month_Year'] = df_filtered['Scheduled At'].dt.strftime('%b-%Y')
            
            # Show all months found in data
            all_months = df_filtered['Month_Year'].unique()
            st.sidebar.write(f"All months in data: {sorted(all_months)}")
            
            # Filter for Sep, Oct, Nov months only
            valid_months = ['Sep-2025', 'Oct-2025', 'Nov-2025']
            available_months = [month for month in df_filtered['Month_Year'].unique() if month in valid_months]
            
            st.sidebar.write(f"Available months after filter: {available_months}")
            
            if not available_months:
                st.warning("No data found for September, October, or November 2025.")
                st.info("Please check if your CSV contains data for these months in 'Scheduled At' column.")
            else:
                selected_month = st.sidebar.selectbox(
                    "Select Month:",
                    options=available_months
                )
                
                # Delivery Hub filter
                available_hubs = df_filtered['Delivery Hub'].unique().tolist()
                selected_hub = st.sidebar.selectbox(
                    "Select Delivery Hub:",
                    options=['All Hubs'] + available_hubs
                )
                
                if selected_month:
                    # Filter data for selected month
                    monthly_data = df_filtered[df_filtered['Month_Year'] == selected_month].copy()
                    
                    # Apply hub filter if not 'All Hubs'
                    if selected_hub != 'All Hubs':
                        monthly_data = monthly_data[monthly_data['Delivery Hub'] == selected_hub]
                    
                    if not monthly_data.empty:
                        # Create summary table
                        summary_data = monthly_data.groupby(['Driver', 'Vehicle', 'Model Name', 'Delivery Hub']).agg({
                            'Shipping Postal Code': lambda x: ', '.join(map(str, x.unique())),
                            'delivered_count': 'sum'
                        }).reset_index()
                        
                        # Display the summary table
                        if selected_hub == 'All Hubs':
                            st.subheader(f"All Hubs Summary for {selected_month}")
                        else:
                            st.subheader(f"{selected_hub} - {selected_month}")
                            
                        st.dataframe(
                            summary_data[['Driver', 'Vehicle', 'Model Name', 'Delivery Hub', 'Shipping Postal Code', 'delivered_count']],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Download button
                        csv = summary_data.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"driver_summary_{selected_month}_{selected_hub.replace(' ', '_')}.csv",
                            mime="text/csv"
                        )
                        
                        # Show some basic metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Drivers", summary_data['Driver'].nunique())
                        with col2:
                            st.metric("Total Delivered", summary_data['delivered_count'].sum())
                        with col3:
                            st.metric("Total Hubs", summary_data['Delivery Hub'].nunique())
                        
                    else:
                        st.warning(f"No data available for {selected_hub} in {selected_month}.")
                
    except Exception as e:
        st.error(f"Error processing the file: {str(e)}")
else:
    st.info("Please upload a CSV file to get started.")