import streamlit as st
from utils.data_manager import DataManager
import pandas as pd

st.set_page_config(page_title="Members Management", page_icon="👥")

# Initialize DataManager
dm = DataManager()

st.title("Members Management")

# Tabs for different member management functions
tab1, tab2 = st.tabs(["Add Member", "View/Edit Members"])

with tab1:
    st.header("Add New Member")
    
    # Member registration form
    with st.form("member_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            
        with col2:
            membership_type = st.selectbox(
                "Membership Type",
                ["Basic", "Premium", "VIP"]
            )
            emergency_contact = st.text_input("Emergency Contact")
            status = st.selectbox("Status", ["Active", "Inactive"])
        
        submit_button = st.form_submit_button("Register Member")
        
        if submit_button:
            if name and email and phone:
                member_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'membership_type': membership_type,
                    'emergency_contact': emergency_contact,
                    'status': status
                }
                
                member_id = dm.add_member(member_data)
                st.success(f"Member {name} successfully registered with ID: {member_id}")
            else:
                st.error("Please fill in all required fields")

with tab2:
    st.header("View/Edit Members")
    
    # Load and display members
    members_df = dm.get_members()
    
    # Search and filter
    search_term = st.text_input("Search Members", "")
    status_filter = st.multiselect(
        "Filter by Status",
        options=members_df['status'].unique(),
        default=members_df['status'].unique()
    )
    
    # Filter dataframe
    filtered_df = members_df[
        (members_df['name'].str.contains(search_term, case=False, na=False)) &
        (members_df['status'].isin(status_filter))
    ]
    
    # Display members table
    st.dataframe(
        filtered_df,
        column_config={
            "id": "Member ID",
            "name": "Name",
            "email": "Email",
            "phone": "Phone",
            "join_date": "Join Date",
            "membership_type": "Membership",
            "status": "Status",
            "emergency_contact": "Emergency Contact"
        },
        hide_index=True
    )
    
    # Edit member
    st.subheader("Edit Member")
    member_to_edit = st.number_input("Enter Member ID to edit", min_value=1, max_value=len(members_df) if len(members_df) > 0 else 1)
    
    if st.button("Load Member Details"):
        member_data = members_df[members_df['id'] == member_to_edit].iloc[0]
        
        with st.form("edit_member"):
            name = st.text_input("Name", value=member_data['name'])
            email = st.text_input("Email", value=member_data['email'])
            phone = st.text_input("Phone", value=member_data['phone'])
            membership_type = st.selectbox(
                "Membership Type",
                ["Basic", "Premium", "VIP"],
                index=["Basic", "Premium", "VIP"].index(member_data['membership_type'])
            )
            status = st.selectbox(
                "Status",
                ["Active", "Inactive"],
                index=["Active", "Inactive"].index(member_data['status'])
            )
            emergency_contact = st.text_input("Emergency Contact", value=member_data['emergency_contact'])
            
            if st.form_submit_button("Update Member"):
                updated_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'membership_type': membership_type,
                    'status': status,
                    'emergency_contact': emergency_contact
                }
                dm.update_member(member_to_edit, updated_data)
                st.success("Member details updated successfully!")
                st.experimental_rerun()

# Export functionality
if not members_df.empty:
    st.download_button(
        label="Export Members Data",
        data=members_df.to_csv(index=False),
        file_name="members_export.csv",
        mime="text/csv"
    )
