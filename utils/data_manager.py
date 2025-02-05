import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.members_file = 'data/members.csv'
        self.attendance_file = 'data/attendance.csv'
        self.finance_file = 'data/finance.csv'
        self.measurements_file = 'data/measurements.csv'
        self._initialize_files()

    def _initialize_files(self):
        # Members CSV
        if not os.path.exists(self.members_file):
            pd.DataFrame(columns=[
                'id', 'name', 'email', 'phone', 'join_date', 
                'membership_type', 'status', 'emergency_contact'
            ]).to_csv(self.members_file, index=False)

        # Attendance CSV
        if not os.path.exists(self.attendance_file):
            pd.DataFrame(columns=[
                'member_id', 'date', 'check_in', 'check_out'
            ]).to_csv(self.attendance_file, index=False)

        # Finance CSV
        if not os.path.exists(self.finance_file):
            pd.DataFrame(columns=[
                'date', 'type', 'category', 'amount', 'description'
            ]).to_csv(self.finance_file, index=False)

        # Measurements CSV
        if not os.path.exists(self.measurements_file):
            pd.DataFrame(columns=[
                'member_id', 'date', 'weight', 'height', 'chest',
                'waist', 'arms', 'legs', 'bmi'
            ]).to_csv(self.measurements_file, index=False)

    def add_member(self, member_data):
        df = pd.read_csv(self.members_file)
        member_data['id'] = len(df) + 1
        member_data['join_date'] = datetime.now().strftime('%Y-%m-%d')
        df = pd.concat([df, pd.DataFrame([member_data])], ignore_index=True)
        df.to_csv(self.members_file, index=False)
        return member_data['id']

    def get_members(self):
        return pd.read_csv(self.members_file)

    def update_member(self, member_id, updated_data):
        df = pd.read_csv(self.members_file)
        df.loc[df['id'] == member_id, list(updated_data.keys())] = list(updated_data.values())
        df.to_csv(self.members_file, index=False)

    def record_attendance(self, member_id, check_in=True):
        df = pd.read_csv(self.attendance_file)
        today = datetime.now().strftime('%Y-%m-%d')
        time_now = datetime.now().strftime('%H:%M:%S')
        
        if check_in:
            new_record = {
                'member_id': member_id,
                'date': today,
                'check_in': time_now,
                'check_out': None
            }
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        else:
            df.loc[(df['member_id'] == member_id) & 
                  (df['date'] == today) & 
                  (df['check_out'].isna()), 'check_out'] = time_now
        
        df.to_csv(self.attendance_file, index=False)

    def add_financial_record(self, record_data):
        df = pd.read_csv(self.finance_file)
        record_data['date'] = datetime.now().strftime('%Y-%m-%d')
        df = pd.concat([df, pd.DataFrame([record_data])], ignore_index=True)
        df.to_csv(self.finance_file, index=False)

    def add_measurements(self, measurement_data):
        df = pd.read_csv(self.measurements_file)
        measurement_data['date'] = datetime.now().strftime('%Y-%m-%d')
        # Calculate BMI
        height_m = measurement_data['height'] / 100  # convert cm to m
        weight_kg = measurement_data['weight']
        measurement_data['bmi'] = weight_kg / (height_m * height_m)
        
        df = pd.concat([df, pd.DataFrame([measurement_data])], ignore_index=True)
        df.to_csv(self.measurements_file, index=False)

    def get_measurements(self, member_id):
        df = pd.read_csv(self.measurements_file)
        return df[df['member_id'] == member_id].sort_values('date')

    def get_financial_summary(self):
        df = pd.read_csv(self.finance_file)
        return df

    def get_attendance_report(self, start_date=None, end_date=None):
        df = pd.read_csv(self.attendance_file)
        if start_date and end_date:
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df
