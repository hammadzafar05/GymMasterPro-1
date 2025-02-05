import streamlit as st
from utils.data_manager import DataManager
from utils.charts import create_attendance_chart
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Attendance Management", page_icon="📋")

# Initialize DataManager
dm = DataManager()

st.title("Attendance Management")

# Tabs for different attendance functions
tab1, tab2 = st.tabs(["Check In/Out", "Attendance Reports"])

with tab1:
    st.header("Member Check In/Out")
    
    # Load members
    members_df = dm.get_members()
    
    col1, col2 = st.columns(2)
    
    with col1:
        member_id = st.selectbox(
            "Select Member",
            options=members_df['id'].tolist(),
            format_func=lambda x: members_df[members_df['id'] == x]['name'].iloc[0]
        )
        
    with col2:
        action = st.radio("Action", ["Check In", "Check Out"])
    
    if st.button("Record Attendance"):
        dm.record_attendance(member_id, action == "Check In")
        st.success(f"Member {members_df[members_df['id'] == member_id]['name'].iloc[0]} {action.lower()}ed successfully!")

with tab2:
    st.header("Attendance Reports")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=7)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now()
        )
    
    # Load attendance data
    attendance_df = dm.get_attendance_report(str(start_date), str(end_date))
    
    if not attendance_df.empty:
        # Attendance chart
        st.plotly_chart(create_attendance_chart(attendance_df, members_df), use_container_width=True)
        
        # Detailed attendance records
        st.subheader("Attendance Records")
        
        # Merge with member names
        detailed_df = pd.merge(
            attendance_df,
            members_df[['id', 'name']],
            left_on='member_id',
            right_on='id'
        )
        
        st.dataframe(
            detailed_df[['date', 'name', 'check_in', 'check_out']].sort_values('date', ascending=False),
            column_config={
                "date": "Date",
                "name": "Member Name",
                "check_in": "Check In Time",
                "check_out": "Check Out Time"
            },
            hide_index=True
        )
        
        # Export functionality
        st.download_button(
            label="Export Attendance Report",
            data=detailed_df.to_csv(index=False),
            file_name=f"attendance_report_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
    else:
        st.info("No attendance records found for the selected date range.")

    # Attendance statistics
    st.subheader("Attendance Statistics")
    if not attendance_df.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_visits = len(attendance_df)
            st.metric("Total Visits", total_visits)
            
        with col2:
            unique_members = attendance_df['member_id'].nunique()
            st.metric("Unique Members", unique_members)
            
        with col3:
            avg_daily_visits = total_visits / (end_date - start_date).days
            st.metric("Average Daily Visits", f"{avg_daily_visits:.1f}")
