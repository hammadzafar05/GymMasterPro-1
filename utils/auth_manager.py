import os
import hashlib
import secrets
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

class AuthManager:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, tenant_id: int, email: str, password: str, name: str, role: str = 'staff') -> dict:
        """Register a new user."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO users (tenant_id, email, password_hash, name, role)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, email, name, role, created_at
                    """,
                    (tenant_id, email, self._hash_password(password), name, role)
                )
                self.conn.commit()
                return cur.fetchone()
            except psycopg2.errors.UniqueViolation:
                self.conn.rollback()
                raise ValueError("Email already registered")

    def login_user(self, email: str, password: str) -> dict:
        """Login a user and create a session."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, tenant_id, email, password_hash, name, role
                FROM users
                WHERE email = %s AND status = 'active'
                """,
                (email,)
            )
            user = cur.fetchone()
            
            if not user or user['password_hash'] != self._hash_password(password):
                raise ValueError("Invalid email or password")
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=1)
            
            cur.execute(
                """
                INSERT INTO sessions (user_id, session_id, expires_at)
                VALUES (%s, %s, %s)
                RETURNING session_id
                """,
                (user['id'], session_id, expires_at)
            )
            self.conn.commit()
            
            return {
                'user_id': user['id'],
                'tenant_id': user['tenant_id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role'],
                'session_id': session_id
            }
    
    def validate_session(self, session_id: str) -> dict:
        """Validate a session and return user info."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT u.id as user_id, u.tenant_id, u.email, u.name, u.role
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_id = %s
                AND s.expires_at > CURRENT_TIMESTAMP
                AND s.is_active = true
                AND u.status = 'active'
                """,
                (session_id,)
            )
            user = cur.fetchone()
            if not user:
                raise ValueError("Invalid or expired session")
            return user
    
    def logout_user(self, session_id: str) -> bool:
        """Logout a user by deactivating their session."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sessions
                SET is_active = false
                WHERE session_id = %s
                """,
                (session_id,)
            )
            self.conn.commit()
            return True

    def get_user_by_id(self, user_id: int) -> dict:
        """Get user details by ID."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, tenant_id, email, name, role, created_at, status
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )
            return cur.fetchone()
