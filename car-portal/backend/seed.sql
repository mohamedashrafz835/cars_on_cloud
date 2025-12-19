CREATE TABLE IF NOT EXISTS cars (
    vin VARCHAR(20) PRIMARY KEY,
    current_km INT,
    oil_last_km INT,
    brake_last_km INT
);

INSERT INTO cars (vin, current_km, oil_last_km, brake_last_km) VALUES
('ABC123', 50000, 30000, 30000),
('DEF456', 25000, 15000, 15000),
('GHI789', 10000, 5000, 5000)
ON CONFLICT (vin) DO NOTHING;
