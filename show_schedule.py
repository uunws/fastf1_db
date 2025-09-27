import fastf1

gp_name = "China"  # Chinese GP
year = 2024

for session_type in ['FP1', 'FP2', 'FP3', 'Q', 'R']:
    try:
        session = fastf1.get_session(year, gp_name, session_type)
        session.load(laps=False, telemetry=False)  # metadata only
        if session.laps.empty:
            print(f"{session_type}: NOT PUBLISHED")
        else:
            print(f"{session_type}: AVAILABLE")
    except Exception as e:
        print(f"{session_type}: NOT AVAILABLE ({str(e)})")
