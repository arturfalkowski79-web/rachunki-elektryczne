import sqlite3

initial_data = [
    ("2026-10-03", "Leroy Merlin (Toruń)", "Korytko elektroinstalacyjne 40/60", 129.87),
    ("2026-10-03", "Leroy Merlin (Toruń)", "Rura karbowana peszel 19x25", 112.98),
    ("2026-10-03", "Leroy Merlin (Toruń)", "Uchwyt do kabli UK-USMP3-900", 39.00),
    ("2026-10-03", "Leroy Merlin (Toruń)", "Przewód YDYp 3x2,5 750V 100m", 579.00),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Przewód ant/sat TRI-SHIELD 113/RG6 (100m)", 179.00),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Pokrywa puszki fi 60 (opak.)", 20.92),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PT S60DFW głęboka łączona", 124.00),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PK 60 podwójna z wkrętami", 75.36),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PK 60 potrójna z wkrętami", 8.06),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PK 60 poczwórna z wkrętami", 15.20),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Poziomica montażowa szara Simon 54", 24.60),
    ("2026-10-07", "ASAJ Sp. z o.o.", "UTP kat. 5e drut krążek 100m", 132.91),
    ("2026-10-07", "ASAJ Sp. z o.o.", "Przewód YDYp 4x1,5 mm2 (100m)", 583.00),
    ("2026-10-13", "Leroy Merlin (Toruń)", "Rura karb. 2-warstwowa ziemna 40/32", 165.00),
    ("2026-10-13", "Leroy Merlin (Toruń)", "Przewód YDYp 3x1,5 750V 100m", 2110.00),
    ("2026-10-13", "Leroy Merlin (Toruń)", "Folia kablowa 200x0,07 niebieska", 75.99),
    ("2026-10-16", "Leroy Merlin (Toruń)", "Korytko elektroinstalacyjne 40/60 (10 szt.)", 432.90),
    ("2026-10-16", "Leroy Merlin (Toruń)", "Rura karbowana 19x25 szara 15m (4 szt.)", 125.96),
    ("2026-10-16", "Leroy Merlin (Toruń)", "Przewód YDYp 3x2,5 750V 100m", 579.00)
]

conn = sqlite3.connect("electric_service.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        store TEXT NOT NULL,
        material TEXT NOT NULL,
        amount REAL NOT NULL
    )
""")
cursor.executemany("INSERT INTO expenses (date, store, material, amount) VALUES (?, ?, ?, ?)", initial_data)
conn.commit()
conn.close()
print("Dane z rachunków zostały pomyślnie załadowane do bazy!")
