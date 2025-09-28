import psycopg2
import fastf1
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")

# Connect to DB
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()


def insert_teams(session):
    teams_inserted = {}
    for code in session.drivers:
        driver = session.get_driver(code)
        team_name = driver['TeamName']

        if team_name not in teams_inserted:
            cur.execute("SELECT id FROM teams WHERE name=%s", (team_name,))
            result = cur.fetchone()
            if result:
                team_id = result[0]
            else:
                cur.execute(
                    "INSERT INTO teams (name) VALUES (%s) RETURNING id",
                    (team_name,)
                )
                team_id = cur.fetchone()[0]
            teams_inserted[team_name] = team_id
    conn.commit()
    return teams_inserted


def insert_drivers(session, teams_inserted):
    drivers_inserted = {}
    for code in session.laps['Driver'].unique():
        driver = session.get_driver(code)
        team_id = teams_inserted[driver['TeamName']]

        cur.execute("SELECT id FROM drivers WHERE code=%s", (code,))
        result = cur.fetchone()
        if result:
            driver_id = result[0]
        else:
            race_number = int(driver['DriverNumber']) if driver.get('DriverNumber') else None
            nationality = driver.get('CountryCode', None)
            cur.execute(
                """
                INSERT INTO drivers (code, first_name, last_name, team_id, race_number, nationality)
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING id
                """,
                (code, driver['FirstName'], driver['LastName'], team_id, race_number, nationality)
            )
            driver_id = cur.fetchone()[0]
        drivers_inserted[code] = driver_id
    conn.commit()
    return drivers_inserted


def insert_event(session):
    event = session.event
    year = event['EventDate'].year
    gp_name = event['EventName']
    country = event['Country']
    date = event['EventDate']

    cur.execute(
        "SELECT id FROM events WHERE year=%s AND gp_name=%s",
        (year, gp_name)
    )
    result = cur.fetchone()
    if result:
        event_id = result[0]
    else:
        cur.execute(
            "INSERT INTO events (year, gp_name, country, date) VALUES (%s,%s,%s,%s) RETURNING id",
            (year, gp_name, country, date)
        )
        event_id = cur.fetchone()[0]
    conn.commit()
    return event_id


def insert_results(session, drivers_inserted, event_id):
    if session.results.empty:
        print(f"No results data for {session.event['EventName']}")
        return

    batch = []
    for _, row in session.results.iterrows():
        driver_code = row['Abbreviation']
        driver_id = drivers_inserted.get(driver_code)
        if not driver_id:
            continue

        # Map FastF1 fields to simplified results table
        position = int(row['Position']) if pd.notnull(row['Position']) else None
        grid = int(row['GridPosition']) if pd.notnull(row['GridPosition']) else None
        points = float(row['Points']) if pd.notnull(row['Points']) else None
        status = row['Status'] if pd.notnull(row['Status']) else None
        total_time = str(row['Time']) if pd.notnull(row['Time']) else None

        batch.append((event_id, driver_id, position, grid, points, status, total_time))

    if batch:
        cur.executemany(
            """
            INSERT INTO results (
                event_id, driver_id, position, grid, points, status, total_time
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            batch
        )
        conn.commit()
        print(f"Inserted {len(batch)} results for {session.event['EventName']}")


# 2024 race list
race_list = [
    ('Bahrain', 'R'), ('Saudi Arabia', 'R'), ('Australia', 'R'),
    ('Japan', 'R'), ('China', 'R'), ('Miami', 'R'),
    ('Emilia Romagna', 'R'), ('Monaco', 'R'), ('Canada', 'R'),
    ('Spain', 'R'), ('Austria', 'R'), ('British', 'R'),
    ('Hungary', 'R'), ('Belgium', 'R'), ('Netherlands', 'R'),
    ('Italian', 'R'), ('Azerbaijan', 'R'), ('Singapore', 'R'),
    ('Austin', 'R'), ('Mexico', 'R'), ('Brazil', 'R'),
    ('Las Vegas', 'R'), ('Qatar', 'R'), ('Abu Dhabi', 'R')
]

for gp_name, session_type in race_list:
    print(f"Processing {gp_name} {session_type}...")
    try:
        session = fastf1.get_session(2024, gp_name, session_type)
        session.load()
    except Exception as e:
        print(f"Failed to load {gp_name}: {e}")
        continue

    event_id = insert_event(session)

    if session.laps.empty:
        print(f"No laps data for {gp_name} {session_type}")
        continue

    teams = insert_teams(session)
    drivers = insert_drivers(session, teams)
    insert_results(session, drivers, event_id)

print("All 2024 races processed successfully!")

cur.close()
conn.close()
