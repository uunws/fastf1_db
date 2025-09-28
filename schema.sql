-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Event table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    year INT,
    gp_name TEXT,
    country TEXT,
    date DATE
);

-- Driver table
CREATE TABLE IF NOT EXISTS drivers (
    id SERIAL PRIMARY KEY,
    code TEXT,
    first_name TEXT,
    last_name TEXT,
    team_id INT REFERENCES teams(id),
    race_number INT,
    nationality TEXT -- use countrycode
);

-- Results table
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    driver_id INT NOT NULL REFERENCES drivers(id),
    position INT,        -- finishing position
    grid INT,            -- starting position
    points FLOAT,        -- points scored
    status TEXT,         -- Finished, DNF, DSQ, etc.
    total_time TEXT      -- race time as string (from 'Time' column in FastF1)
);