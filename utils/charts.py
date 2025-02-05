import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_attendance_chart(attendance_df, members_df):
    # Merge attendance with member names
    df = pd.merge(attendance_df, members_df[['id', 'name']], 
                 left_on='member_id', right_on='id')
    
    # Group by date and count
    daily_attendance = df.groupby('date').size().reset_index(name='count')
    
    fig = px.line(daily_attendance, x='date', y='count',
                  title='Daily Attendance',
                  labels={'count': 'Number of Members', 'date': 'Date'})
    
    return fig

def create_financial_chart(finance_df):
    # Group by date and type
    daily_summary = finance_df.groupby(['date', 'type'])['amount'].sum().reset_index()
    
    fig = px.line(daily_summary, x='date', y='amount', color='type',
                  title='Financial Summary',
                  labels={'amount': 'Amount ($)', 'date': 'Date'})
    
    return fig

def create_measurement_progress_chart(measurements_df, metric):
    fig = px.line(measurements_df, x='date', y=metric,
                  title=f'{metric.capitalize()} Progress Over Time',
                  labels={metric: metric.capitalize(), 'date': 'Date'})
    
    return fig

def create_bmi_gauge(bmi_value):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "BMI"},
        gauge = {
            'axis': {'range': [None, 40]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 18.5], 'color': "lightgray"},
                {'range': [18.5, 25], 'color': "green"},
                {'range': [25, 30], 'color': "yellow"},
                {'range': [30, 40], 'color': "red"}
            ],
        }
    ))
    
    return fig

def create_membership_distribution_pie(members_df):
    membership_counts = members_df['membership_type'].value_counts()
    
    fig = px.pie(values=membership_counts.values, 
                 names=membership_counts.index,
                 title='Membership Distribution')
    
    return fig
