import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "electric_service.db"

# Inicjalizacja bazy danych i automatyczne dodanie danych początkowych
def init_expenses_db():
    conn = sqlite3.connect(DB_NAME)
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
    
    # Sprawdź, czy tabela jest pusta – jeśli tak, dodaj początkowe rachunki
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]
    
    if count == 0:
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
        cursor.executemany("INSERT INTO expenses (date, store, material, amount) VALUES (?, ?, ?, ?)", initial_data)
        conn.commit()
        
    conn.close()

# Pobieranie danych z bazy
def get_expenses(store_filter="Wszystkie"):
    conn = sqlite3.connect(DB_NAME)
    if store_filter == "Wszystkie":
        df = pd.read_sql_query(
            "SELECT id, date AS Data, store AS Sklep, material AS Materiał, amount AS 'Wartość (PLN)' FROM expenses ORDER BY date DESC", 
            conn
        )
    else:
        df = pd.read_sql_query(
            "SELECT id, date AS Data, store AS Sklep, material AS Materiał, amount AS 'Wartość (PLN)' FROM expenses WHERE store = ? ORDER BY date DESC", 
            conn, 
            params=(store_filter,)
        )
    conn.close()
    return df

# Dodawanie pojedynczego wydatku
def add_expense(date, store, material, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, store, material, amount) VALUES (?, ?, ?, ?)", (date, store, material, amount))
    conn.commit()
    conn.close()

# Główna funkcja modułu
def render_expenses_tab():
    init_expenses_db()
    
    st.header("🧾 Rejestr Wydatków i Materiałów")
    st.write("Kontrola kosztów z paragonów i faktur za materiały elektryczne.")

    # Sekcja dodawania nowego zakupu
    with st.expander("➕ Dodaj nowy zakup (paragon / faktura)", expanded=False):
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                exp_date = st.date_input("Data zakupu", value=datetime.today())
                exp_store = st.selectbox("Sklep / Sprzedawca", ["Leroy Merlin (Toruń)", "ASAJ Sp. z o.o.", "Inny"])
            with col2:
                exp_material = st.text_input("Nazwa materiału / pozycja")
                exp_amount = st.number_input("Wartość (Brutto PLN)", min_value=0.0, format="%.2f")
            
            submitted = st.form_submit_button("Zapisz w bazie")
            if submitted:
                if not exp_material.strip():
                    st.error("Podaj nazwę materiału!")
                else:
                    add_expense(str(exp_date), exp_store, exp_material, exp_amount)
                    st.success("Dodano pomyślnie do bazy!")
                    st.rerun()

    # Filtrowanie i wyświetlanie danych
    stores = ["Wszystkie", "Leroy Merlin (Toruń)", "ASAJ Sp. z o.o.", "Inny"]
    selected_store = st.selectbox("Filtruj według sklepu", stores)

    df = get_expenses(selected_store)

    if not df.empty:
        total_cost = df["Wartość (PLN)"].sum()
        
        m1, m2 = st.columns(2)
        m1.metric(label="Łączny koszt materiałów", value=f"{total_cost:.2f} PLN")
        m2.metric(label="Liczba pozycji", value=len(df))

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Przycisk do pobierania danych (CSV / Excel kompatybilny)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Pobierz zestawienie (CSV / Excel)",
            data=csv,
            file_name="wydatki_elektryczne.csv",
            mime="text/csv",
        )
    else:
        st.info("Brak wpisów w bazie dla wybranego filtra.")

if __name__ == "__main__":
    render_expenses_tab()
