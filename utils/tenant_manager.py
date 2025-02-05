import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class TenantManager:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        
    def create_tenant(self, name: str, subdomain: str) -> dict:
        """Create a new tenant (gym) in the system."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO tenants (name, subdomain)
                VALUES (%s, %s)
                RETURNING id, name, subdomain, created_at, status
                """,
                (name, subdomain)
            )
            self.conn.commit()
            return cur.fetchone()
    
    def get_tenant_by_subdomain(self, subdomain: str) -> dict:
        """Get tenant details by subdomain."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, name, subdomain, created_at, status, settings
                FROM tenants
                WHERE subdomain = %s
                """,
                (subdomain,)
            )
            return cur.fetchone()
    
    def update_tenant_settings(self, tenant_id: int, settings: dict) -> bool:
        """Update tenant settings."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tenants
                SET settings = settings || %s::jsonb
                WHERE id = %s
                """,
                (settings, tenant_id)
            )
            self.conn.commit()
            return True
    
    def list_tenants(self) -> list:
        """List all tenants in the system."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, name, subdomain, created_at, status
                FROM tenants
                ORDER BY created_at DESC
                """
            )
            return cur.fetchall()
    
    def validate_tenant_access(self, tenant_id: int) -> bool:
        """Validate if a tenant exists and is active."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT status FROM tenants
                WHERE id = %s AND status = 'active'
                """,
                (tenant_id,)
            )
            return cur.fetchone() is not None
