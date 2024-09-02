import sqlite3

conn = sqlite3.connect("emergency_db.sqlite")
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS emergencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emergency_type TEXT NOT NULL,
    instructions TEXT NOT NULL
)
"""
)

cursor.execute(
    """
INSERT INTO emergencies (emergency_type, instructions) VALUES
('not breathing', 'Perform CPR: Press on the chest and give mouth-to-mouth.'),
('bleeding', 'Apply pressure to the wound and keep the injured part elevated.'),
('choking', 'Perform the Heimlich maneuver by applying pressure to the abdomen.'),
('burns', 'Cool the burn under cool running water for at least 10 minutes. Do not apply ice.'),
('fracture', 'Immobilize the affected area. Do not try to realign the bone. Seek medical attention immediately.'),
('heart attack', 'Have the person sit down and rest. Loosen any tight clothing. Administer aspirin if available. Call emergency services.'),
('stroke', 'Remember FAST: Face drooping, Arm weakness, Speech difficulty, Time to call emergency services.'),
('poisoning', 'Try to identify the poison and call the Poison Control Center immediately. Do not induce vomiting unless instructed by a professional.'),
('seizure', 'Do not restrain the person. Remove any nearby objects that might cause injury. Turn the person onto their side and place something soft under their head.'),
('hypothermia', 'Move the person to a warm place. Remove any wet clothing and cover them with warm blankets. Offer warm liquids if they are conscious.')
"""
)

conn.commit()
conn.close()

print("Database and table created, and data inserted successfully.")
