import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Dict, Any, List

# Database configuration
# In production, these should be stored in environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "agro_geospatial")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    """
    Get a connection to the PostgreSQL database.
    
    Returns:
    - Database connection object
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        # In a real app, this would log the error and possibly retry
        print(f"Error connecting to database: {str(e)}")
        # For now, return None to indicate failure
        return None

def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return the results.
    
    Parameters:
    - query: SQL query string
    - params: Query parameters
    
    Returns:
    - List of dictionaries containing query results
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
    except Exception as e:
        # In a real app, this would log the error
        print(f"Error executing query: {str(e)}")
        return []
    finally:
        conn.close()

def execute_update(query: str, params: tuple = None) -> int:
    """
    Execute a SQL update query and return the number of affected rows.
    
    Parameters:
    - query: SQL query string
    - params: Query parameters
    
    Returns:
    - Number of affected rows
    """
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        # In a real app, this would log the error
        print(f"Error executing update: {str(e)}")
        conn.rollback()
        return 0
    finally:
        conn.close()