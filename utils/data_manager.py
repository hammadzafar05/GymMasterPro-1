import pandas as pd
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import pandas as pd

class DataManager:
    def __init__(self, tenant_id: int = None):
        self.tenant_id = tenant_id
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])

    def _check_tenant(self):
        """Ensure tenant_id is set before operations."""
        if not self.tenant_id:
            raise ValueError("Tenant ID is required for this operation")

    def add_member(self, member_data: dict) -> int:
        """Add a new member for the current tenant."""
        self._check_tenant()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO members (
                    tenant_id, name, email, phone,
                    membership_type, status, emergency_contact
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
                """,
                (
                    self.tenant_id, member_data['name'], member_data['email'],
                    member_data['phone'], member_data['membership_type'],
                    member_data['status'], member_data['emergency_contact']
                )
            )
            self.conn.commit()
            return cur.fetchone()[0]

    def get_members(self) -> pd.DataFrame:
        """Get all members for the current tenant."""
        self._check_tenant()
        query = """
            SELECT id, name, email, phone, join_date,
                   membership_type, status, emergency_contact
            FROM members
            WHERE tenant_id = %s
        """
        return pd.read_sql_query(query, self.conn, params=(self.tenant_id,))

    def update_member(self, member_id: int, updated_data: dict):
        """Update member details."""
        self._check_tenant()
        fields = ', '.join([f"{k} = %s" for k in updated_data.keys()])
        values = list(updated_data.values())
        values.extend([self.tenant_id, member_id])

        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE members
                SET {fields}
                WHERE tenant_id = %s AND id = %s
                """,
                values
            )
            self.conn.commit()

    def record_attendance(self, member_id: int, check_in: bool = True):
        """Record member attendance."""
        self._check_tenant()
        today = datetime.now().date()
        current_time = datetime.now().time()

        with self.conn.cursor() as cur:
            if check_in:
                cur.execute(
                    """
                    INSERT INTO attendance (tenant_id, member_id, date, check_in)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (self.tenant_id, member_id, today, current_time)
                )
            else:
                cur.execute(
                    """
                    UPDATE attendance
                    SET check_out = %s
                    WHERE tenant_id = %s 
                    AND member_id = %s 
                    AND date = %s 
                    AND check_out IS NULL
                    """,
                    (current_time, self.tenant_id, member_id, today)
                )
            self.conn.commit()

    def get_attendance_report(self, start_date=None, end_date=None) -> pd.DataFrame:
        """Get attendance report for the current tenant."""
        self._check_tenant()
        query = """
            SELECT a.date, a.check_in, a.check_out, m.name as member_name
            FROM attendance a
            JOIN members m ON a.member_id = m.id
            WHERE a.tenant_id = %s
        """
        params = [self.tenant_id]

        if start_date and end_date:
            query += " AND a.date BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        return pd.read_sql_query(query, self.conn, params=params)

    def add_financial_record(self, record_data: dict):
        """Add a financial record for the current tenant."""
        self._check_tenant()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO finance (
                    tenant_id, date, type, category, amount, description
                ) VALUES (%s, CURRENT_DATE, %s, %s, %s, %s)
                """,
                (
                    self.tenant_id, record_data['type'], record_data['category'],
                    record_data['amount'], record_data['description']
                )
            )
            self.conn.commit()

    def get_financial_summary(self) -> pd.DataFrame:
        """Get financial summary for the current tenant."""
        self._check_tenant()
        query = """
            SELECT date, type, category, amount, description
            FROM finance
            WHERE tenant_id = %s
            ORDER BY date DESC
        """
        return pd.read_sql_query(query, self.conn, params=(self.tenant_id,))

    def add_measurements(self, measurement_data: dict):
        """Add measurements for a member."""
        self._check_tenant()
        height_m = measurement_data['height'] / 100
        bmi = measurement_data['weight'] / (height_m * height_m)

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO measurements (
                    tenant_id, member_id, date, weight, height,
                    chest, waist, arms, legs, bmi
                ) VALUES (%s, %s, CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    self.tenant_id, measurement_data['member_id'],
                    measurement_data['weight'], measurement_data['height'],
                    measurement_data['chest'], measurement_data['waist'],
                    measurement_data['arms'], measurement_data['legs'], bmi
                )
            )
            self.conn.commit()

    def get_measurements(self, member_id: int) -> pd.DataFrame:
        """Get measurements history for a member."""
        self._check_tenant()
        query = """
            SELECT date, weight, height, chest, waist, arms, legs, bmi
            FROM measurements
            WHERE tenant_id = %s AND member_id = %s
            ORDER BY date
        """
        return pd.read_sql_query(query, self.conn, params=(self.tenant_id, member_id))

    def get_data(self) -> tuple:
        """Get all necessary data for the dashboard."""
        self._check_tenant()

        # Get members data
        members_query = """
            SELECT id, name, email, phone, join_date,
                   membership_type, status, emergency_contact
            FROM members
            WHERE tenant_id = %s
        """

        # Get finance data
        finance_query = """
            SELECT date, type, category, amount, description
            FROM finance
            WHERE tenant_id = %s
            ORDER BY date DESC
        """

        # Get attendance data
        attendance_query = """
            SELECT a.date, a.check_in, a.check_out, m.name as member_name, a.member_id
            FROM attendance a
            JOIN members m ON a.member_id = m.id
            WHERE a.tenant_id = %s
        """

        try:
            members_df = pd.read_sql_query(members_query, self.conn, params=(self.tenant_id,))
            finance_df = pd.read_sql_query(finance_query, self.conn, params=(self.tenant_id,))
            attendance_df = pd.read_sql_query(attendance_query, self.conn, params=(self.tenant_id,))
            return members_df, finance_df, attendance_df
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()