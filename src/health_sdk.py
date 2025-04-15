import psycopg2
from requests_oauthlib import OAuth2Session
from datetime import datetime
import os

# Configuration - Replace with your credentials
SAMSUNG_CLIENT_ID = os.environ.get("SAMSUNG_CLIENT_ID")
SAMSUNG_CLIENT_SECRET = os.environ.get("SAMSUNG_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
DATABASE_URL = os.environ.get("DATABASE_URL")

# Samsung Health API endpoints (hypothetical - check actual documentation)
API_BASE_URL = "https://api.shealth.samsung.com"
AUTHORIZATION_URL = f"{API_BASE_URL}/oauth2/authorize"
TOKEN_URL = f"{API_BASE_URL}/oauth2/token"
SCOPES = [
    "health.heart_rate.read",
    "health.oxygen.read",
    "health.stress.read",
    "health.exercise.read",
    "health.blood_pressure.read",
    "health.glucose.read"
]

# Database setup
def create_tables():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS heart_rate (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            value INTEGER,
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blood_oxygen (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            value INTEGER,
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stress_level (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            value INTEGER,
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercise_sessions (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            activity_type VARCHAR(50),
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration INTEGER,
            calories INTEGER,
            max_heart_rate INTEGER,
            avg_heart_rate INTEGER
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blood_pressure (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            systolic INTEGER,
            diastolic INTEGER,
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS glucose (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            value INTEGER,
            measurement_type VARCHAR(50),
            timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

# Samsung Health API client
class SamsungHealthClient:
    def __init__(self):
        self.oauth = OAuth2Session(
            client_id=SAMSUNG_CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            scope=SCOPES
        )
        
    def get_auth_url(self):
        return self.oauth.authorization_url(AUTHORIZATION_URL)
    
    def fetch_token(self, authorization_response):
        return self.oauth.fetch_token(
            TOKEN_URL,
            authorization_response=authorization_response,
            client_secret=SAMSUNG_CLIENT_SECRET
        )
    
    def get_heart_rate(self):
        return self.oauth.get(f"{API_BASE_URL}/v1/health/heartrate").json()
    
    def get_blood_oxygen(self):
        return self.oauth.get(f"{API_BASE_URL}/v1/health/oxygen").json()
    
    def get_stress_level(self):
        return self.oauth.get(f"{API_BASE_URL}/v1/health/stress").json()

    def get_exercise_sessions(self, start_date, end_date):
        return self.oauth.get(
            f"{API_BASE_URL}/v1/health/exercise",
            params={"start": start_date, "end": end_date}
        ).json()

    def get_blood_pressure(self):
        return self.oauth.get(f"{API_BASE_URL}/v1/health/bloodpressure").json()

    def get_glucose(self):
        return self.oauth.get(f"{API_BASE_URL}/v1/health/glucose").json()

# Database operations
def save_health_data(data, table_name):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    for entry in data:
        cur.execute(f"""
            INSERT INTO {table_name} (user_id, value, timestamp)
            VALUES (%s, %s, %s)
        """, (
            entry['user_id'],
            entry['value'],
            datetime.fromisoformat(entry['timestamp'])
        ))
    
    conn.commit()
    cur.close()
    conn.close()

def save_exercise_data(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    for session in data['sessions']:
        cur.execute("""
            INSERT INTO exercise_sessions 
            (user_id, activity_type, start_time, end_time, duration, calories, max_heart_rate, avg_heart_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            session['activity_type'],
            datetime.fromisoformat(session['start_time']),
            datetime.fromisoformat(session['end_time']),
            session['duration'],
            session['calories'],
            session.get('max_heart_rate'),
            session.get('avg_heart_rate')
        ))
    
    conn.commit()
    cur.close()
    conn.close()

def save_blood_pressure_data(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    for entry in data['items']:
        cur.execute("""
            INSERT INTO blood_pressure 
            (user_id, systolic, diastolic, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (
            entry['user_id'],
            entry['systolic'],
            entry['diastolic'],
            datetime.fromisoformat(entry['timestamp'])
        ))
    
    conn.commit()
    cur.close()
    conn.close()

def save_glucose_data(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    for entry in data['items']:
        cur.execute("""
            INSERT INTO glucose 
            (user_id, value, measurement_type, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (
            entry['user_id'],
            entry['value'],
            entry.get('measurement_type', 'unknown'),
            datetime.fromisoformat(entry['timestamp'])
        ))
    
    conn.commit()
    cur.close()
    conn.close()

# Main flow
def main():
    create_tables()
    
    client = SamsungHealthClient()
    
    # Authenticate (you'll need to implement the callback handler)
    print("Authorize at:", client.get_auth_url())
    authorization_response = input("Enter callback URL: ")
    client.fetch_token(authorization_response)
    
    # Fetch data
    heart_rate_data = client.get_heart_rate()
    blood_oxygen_data = client.get_blood_oxygen()
    stress_data = client.get_stress_level()

    today = datetime.now().date().isoformat()
    
    exercise_data = client.get_exercise_sessions(today, today)
    blood_pressure_data = client.get_blood_pressure()
    glucose_data = client.get_glucose()
    
    # Save to database
    save_health_data(heart_rate_data['items'], 'heart_rate')
    save_health_data(blood_oxygen_data['items'], 'blood_oxygen')
    save_health_data(stress_data['items'], 'stress_level')
    save_exercise_data(exercise_data)
    save_blood_pressure_data(blood_pressure_data)
    save_glucose_data(glucose_data)

if __name__ == "__main__":
    main()
