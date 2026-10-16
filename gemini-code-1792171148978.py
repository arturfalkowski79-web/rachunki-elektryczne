import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "electric_service.db"

# Inicjalizacja bazy danych i tabeli
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
    else:
        st.info("Brak wpisów w bazie dla wybranego filtra.")

if __name__ == "__main__":
    render_expenses_tab()