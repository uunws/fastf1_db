# import fastf1

# gp_name = "China"  # Chinese GP
# year = 2024

# for session_type in ['FP1', 'FP2', 'FP3', 'Q', 'R']:
#     try:
#         session = fastf1.get_session(year, gp_name, session_type)
#         session.load(laps=False, telemetry=False)  # metadata only
#         if session.laps.empty:
#             print(f"{session_type}: NOT PUBLISHED")
#         else:
#             print(f"{session_type}: AVAILABLE")
#     except Exception as e:
#         print(f"{session_type}: NOT AVAILABLE ({str(e)})")

import fastf1
# schedule = fastf1.events.get_event_schedule(2024)
# print(schedule[['RoundNumber', 'EventName', 'Country', 'EventDate']])

import pandas as pd

# Example: load a session (Race session)
year = 2024
gp_name = 'Bahrain'
session_type = 'R'

session = fastf1.get_session(year, gp_name, session_type)
session.load()

# # 1️⃣ Check driver info
# print("=== Driver Info Check ===")
# driver_columns = ['Number', 'Nationality', 'FirstName', 'LastName', 'TeamName']
# for code in session.drivers:
#     driver = session.get_driver(code)
#     missing = [col for col in driver_columns if col not in driver or pd.isnull(driver.get(col))]
#     if missing:
#         print(f"Driver {code} missing: {missing}")

# # 2️⃣ Check results info
# print("\n=== Results Check ===")
# if session.results.empty:
#     print("No results available for this session")
# else:
#     results_columns = ['Position', 'GridPosition', 'Points', 'Status', 'Laps', 'Time', 'FastestLap', 'FastestLapRank']
#     for col in results_columns:
#         if col not in session.results.columns:
#             print(f"Column missing entirely: {col}")
#         else:
#             null_count = session.results[col].isnull().sum()
#             if null_count > 0:
#                 print(f"Column {col} has {null_count} NULL values")

print("=== Driver keys ===")
for code in session.drivers:
    driver = session.get_driver(code)
    print(f"{code}: {list(driver.keys())}")

print("\n=== Results columns ===")
print(session.results.columns.tolist())

for _, row in session.results.iterrows():
    print(row['Abbreviation'], row['Position'], row['GridPosition'], row['Points'], row['Status'], row['Time'])


print(session.results.columns)   # Columns available
print(session.results.head())    # Actual data