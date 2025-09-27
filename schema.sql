-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    country TEXT
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
    team_id INT REFERENCES teams(id)
);

-- Result table
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(id),
    driver_id INT REFERENCES drivers(id),
    position INT,         -- finishing position in the race
    grid INT,             -- starting position
    points FLOAT,         -- points scored
    fastest_lap INTERVAL  -- fastest lap of the driver (optional)
);
