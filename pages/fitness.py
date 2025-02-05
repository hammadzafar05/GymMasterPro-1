import streamlit as st
from utils.data_manager import DataManager
from utils.charts import create_measurement_progress_chart, create_bmi_gauge
import pandas as pd

st.set_page_config(page_title="Fitness Tracking", page_icon="📊")

# Initialize DataManager
dm = DataManager()

st.title("Fitness Tracking")

# Load members for selection
members_df = dm.get_members()

# Member selection
member_id = st.selectbox(
    "Select Member",
    options=members_df['id'].tolist(),
    format_func=lambda x: members_df[members_df['id'] == x]['name'].iloc[0]
)

# Tabs for different fitness tracking functions
tab1, tab2 = st.tabs(["Record Measurements", "Progress Tracking"])

with tab1:
    st.header("Record New Measurements")
    
    with st.form("measurements_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0)
            height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0)
            chest = st.number_input("Chest (cm)", min_value=0.0, max_value=200.0)
            
        with col2:
            waist = st.number_input("Waist (cm)", min_value=0.0, max_value=200.0)
            arms = st.number_input("Arms (cm)", min_value=0.0, max_value=100.0)
            legs = st.number_input("Legs (cm)", min_value=0.0, max_value=200.0)
        
        if st.form_submit_button("Record Measurements"):
            if weight > 0 and height > 0:
                measurement_data = {
                    'member_id': member_id,
                    'weight': weight,
                    'height': height,
                    'chest': chest,
                    'waist': waist,
                    'arms': arms,
                    'legs': legs
                }
                dm.add_measurements(measurement_data)
                st.success("Measurements recorded successfully!")
            else:
                st.error("Please enter valid measurements")

with tab2:
    st.header("Progress Tracking")
    
    # Load measurements for selected member
    measurements_df = dm.get_measurements(member_id)
    
    if not measurements_df.empty:
        # Latest measurements
        latest_measurements = measurements_df.iloc[-1]
        
        # BMI Gauge
        st.subheader("Current BMI")
        st.plotly_chart(create_bmi_gauge(latest_measurements['bmi']), use_container_width=True)
        
        # Progress charts
        metrics = ['weight', 'chest', 'waist', 'arms', 'legs']
        
        for metric in metrics:
            st.plotly_chart(
                create_measurement_progress_chart(measurements_df, metric),
                use_container_width=True
            )
        
        # Measurements history
        st.subheader("Measurements History")
        st.dataframe(
            measurements_df.sort_values('date', ascending=False),
            column_config={
                "date": "Date",
                "weight": "Weight (kg)",
                "height": "Height (cm)",
                "chest": "Chest (cm)",
                "waist": "Waist (cm)",
                "arms": "Arms (cm)",
                "legs": "Legs (cm)",
                "bmi": "BMI"
            },
            hide_index=True
        )
        
        # Export functionality
        st.download_button(
            label="Export Measurements History",
            data=measurements_df.to_csv(index=False),
            file_name=f"measurements_history_member_{member_id}.csv",
            mime="text/csv"
        )
    else:
        st.info("No measurements recorded for this member yet.")