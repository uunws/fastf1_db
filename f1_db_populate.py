import psycopg2
import fastf1
from fastf1 import events
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import fastf1.plotting
import io
import os
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv("DB_URL")

# Connect to DB
conn = psycopg2.connect(DB_URL)

cur = conn.cursor()


def insert_teams(session):
    teams_inserted = {}
    for code in session.drivers:  # driver code strings
        driver = session.get_driver(code)  # now driver is a dict
        team_name = driver['TeamName']
        if team_name not in teams_inserted:
            # Check if team already exists
            cur.execute("SELECT id FROM teams WHERE name=%s", (team_name,))
            result = cur.fetchone()
            if result:
                team_id = result[0]
            else:
                cur.execute("INSERT INTO teams (name) VALUES (%s) RETURNING id", (team_name,))
                team_id = cur.fetchone()[0]
            teams_inserted[team_name] = team_id
    conn.commit()
    return teams_inserted


def insert_drivers(session, teams_inserted):
    drivers_inserted = {}
    for code in session.laps['Driver'].unique():
        driver = session.get_driver(code)
        team_id = teams_inserted[driver['TeamName']]
        # Check if driver exists
        cur.execute("SELECT id FROM drivers WHERE code=%s", (code,))
        result = cur.fetchone()
        if result:
            driver_id = result[0]
        else:
            cur.execute(
                "INSERT INTO drivers (code, first_name, last_name, team_id) VALUES (%s,%s,%s,%s) RETURNING id",
                (code, driver['FirstName'], driver['LastName'], team_id)
            )
            driver_id = cur.fetchone()[0]
        drivers_inserted[code] = driver_id
    conn.commit()
    return drivers_inserted


def insert_event(session):
    event = session.event
    # Check if event exists
    cur.execute(
        "SELECT id FROM events WHERE year=%s AND gp_name=%s",
        (event.year, event['EventName'])
    )
    result = cur.fetchone()
    if result:
        event_id = result[0]
    else:
        # print(event)
        # print(event.index)
        cur.execute(
            "INSERT INTO events (year, gp_name, country, date) VALUES (%s,%s,%s,%s) RETURNING id",
            (event.year, event['EventName'], event['Country'], event['EventDate'])
        )
        event_id = cur.fetchone()[0]
    conn.commit()
    return event_id

def insert_results(session, drivers_inserted, event_id):
    """
    Insert race results into the results table efficiently.
    """
    print(session.results.columns)

    if session.results.empty:
        print(f"No results data for {session.event['EventName']} Race")
        return

    batch = []
    for _, row in session.results.iterrows():
        driver_code = row['Abbreviation']
        driver_id = drivers_inserted.get(driver_code)
        if not driver_id:
            continue

        # Handle optional data
        position = int(row['Position']) if pd.notnull(row['Position']) else None
        grid = int(row['GridPosition']) if pd.notnull(row['GridPosition']) else None
        points = float(row['Points']) if pd.notnull(row['Points']) else None
        fastest_lap = row['Time'] if pd.notnull(row['Time']) else None

        batch.append((event_id, driver_id, position, grid, points, fastest_lap))

    if batch:
        cur.executemany(
            """
            INSERT INTO results (event_id, driver_id, position, grid, points, fastest_lap)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            batch
        )
        conn.commit()
        print(f"Inserted {len(batch)} results for {session.event['EventName']}")


# 2024 schedule only
race_list = [
    ('Bahrain', 'R'),
    ('Saudi Arabia', 'R'),
    ('Australia', 'R'),
    ('Japan', 'R'),
    ('China', 'R'),
    ('Miami', 'R'),
    ('Emilia Romagna', 'R'),
    ('Monaco', 'R'),
    ('Canada', 'R'),
    ('Spain', 'R'),
    ('Austria', 'R'),
    ('Britain', 'R'),
    ('Hungary', 'R'),
    ('Belgium', 'R'),
    ('Netherlands', 'R'),
    ('Italy', 'R'),
    ('Azerbaijan', 'R'),
    ('Singapore', 'R'),
    ('USA', 'R'),
    ('Mexico', 'R'),
    ('Brazil', 'R'),
    ('Las Vegas', 'R'),
    ('Qatar', 'R'),
    ('Abu Dhabi', 'R')
]

INSERT_TELEMETRY = False

for gp_name, session_type in race_list:
    print(f"Processing {gp_name} {session_type}...")
    session = fastf1.get_session(2024, gp_name, session_type)
    session.load()  # this may take a few seconds
    if session.laps.empty:
        print(f"No laps data for {gp_name} {session_type}")
        continue
    teams = insert_teams(session)
    drivers = insert_drivers(session, teams)
    event_id = insert_event(session)
    insert_results(session, drivers, event_id)

print("All 2024 races processed successfully!")

# Close DB connection
cur.close()
conn.close()

# # Example: Fetch 2024 Bahrain GP data
# session = fastf1.get_session(2024, 'Bahrain', 'R')
# session.load()
# russel = session.get_driver('RUS')
# norris = session.get_driver('NOR')

# fast_leclerc = session.laps.pick_drivers('LEC').pick_fastest()
# lec_car_data = fast_leclerc.get_car_data()
# t = lec_car_data['Time']
# vCar = lec_car_data['Speed']

# # The rest is just plotting
# fig, ax = plt.subplots()
# ax.plot(t, vCar, label='Fast')
# ax.set_xlabel('Time')
# ax.set_ylabel('Speed [Km/h]')
# ax.set_title('Leclerc is')
# ax.legend()
# plt.show()

# print("-----see session-----")
# print(session.drivers)
# print("-------drivers-------")
# print(russel['FirstName'])
# print(norris['FirstName'])
# print("---------------------")


