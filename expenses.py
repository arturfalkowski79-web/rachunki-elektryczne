import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import tempfile
import os

DB_NAME = "electric_service.db"

# Inicjalizacja bazy danych i danych początkowych
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
    
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_data = [
            ("2026-10-03", "Leroy Merlin (Torun)", "Korytko elektroinstalacyjne 40/60", 129.87),
            ("2026-10-03", "Leroy Merlin (Torun)", "Rura karbowana peszel 19x25", 112.98),
            ("2026-10-03", "Leroy Merlin (Torun)", "Uchwyt do kabli UK-USMP3-900", 39.00),
            ("2026-10-03", "Leroy Merlin (Torun)", "Przewód YDYp 3x2,5 750V 100m", 579.00),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Przewód ant/sat TRI-SHIELD 113/RG6 (100m)", 179.00),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Pokrywa puszki fi 60 (opak.)", 20.92),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PT S60DFW głęboka łączona", 124.00),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PK 60 podwójna z wkrętami", 75.36),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PK 60 potrójna z wkrętami", 8.06),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Puszka PK 60 poczwórna z wkrętami", 15.20),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Poziomica montażowa szara Simon 54", 24.60),
            ("2026-10-07", "ASAJ Sp. z o.o.", "UTP kat. 5e drut krążek 100m", 132.91),
            ("2026-10-07", "ASAJ Sp. z o.o.", "Przewód YDYp 4x1,5 mm2 (100m)", 583.00),
            ("2026-10-13", "Leroy Merlin (Torun)", "Rura karb. 2-warstwowa ziemna 40/32", 165.00),
            ("2026-10-13", "Leroy Merlin (Torun)", "Przewód YDYp 3x1,5 750V 100m", 2110.00),
            ("2026-10-13", "Leroy Merlin (Torun)", "Folia kablowa 200x0,07 niebieska", 75.99),
            ("2026-10-16", "Leroy Merlin (Torun)", "Korytko elektroinstalacyjne 40/60 (10 szt.)", 432.90),
            ("2026-10-16", "Leroy Merlin (Torun)", "Rura karbowana 19x25 szara 15m (4 szt.)", 125.96),
            ("2026-10-16", "Leroy Merlin (Torun)", "Przewód YDYp 3x2,5 750V 100m", 579.00)
        ]
        cursor.executemany("INSERT INTO expenses (date, store, material, amount) VALUES (?, ?, ?, ?)", initial_data)
        conn.commit()
        
    conn.close()

# Pobieranie danych posortowanych rosnąco (od najstarszych do najnowszych: ASC)
def get_expenses(store_filter="Wszystkie"):
    conn = sqlite3.connect(DB_NAME)
    if store_filter == "Wszystkie":
        df = pd.read_sql_query(
            "SELECT id, date AS Data, store AS Sklep, material AS Materiał, amount AS 'Wartość (PLN)' FROM expenses ORDER BY date ASC, id ASC", 
            conn
        )
    else:
        df = pd.read_sql_query(
            "SELECT id, date AS Data, store AS Sklep, material AS Materiał, amount AS 'Wartość (PLN)' FROM expenses WHERE store = ? ORDER BY date ASC, id ASC", 
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

# Funkcja usuwająca polskie znaki na potrzeby czcionek standardowych PDF
def clean_text(text):
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# Klasa generująca PDF
class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 14)
        self.cell(0, 8, "ZESTAWIENIE KOSZTOW MATERIALOW ELEKTRYCZNYCH", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Strona {self.page_no()}", 0, 0, "C")

def generate_pdf_report(df, contractor, investor, order_title):
    pdf = PDFReport()
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, clean_text(f"Zlecenie: {order_title}"), 0, 1)
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, clean_text(f"Wykonawca: {contractor}"), 0, 1)
    pdf.cell(0, 5, clean_text(f"Inwestor: {investor}"), 0, 1)
    pdf.cell(0, 5, f"Data wygenerowania: {datetime.today().strftime('%Y-%m-%d')}", 0, 1)
    pdf.ln(5)

    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(230, 230, 230)
    
    cols = [25, 45, 95, 30]
    headers = ["Data", "Sklep", "Material", "Wartosc (PLN)"]
    
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 7, clean_text(h), 1, 0, "C", True)
    pdf.ln()

    pdf.set_font("helvetica", "", 8)
    total = 0
    for _, row in df.iterrows():
        date_str = clean_text(str(row["Data"]))
        store_str = clean_text(str(row["Sklep"]))[:25]
        mat_str = clean_text(str(row["Materiał"]))[:55]
        val_str = f"{row['Wartość (PLN)']:.2f}"
        
        pdf.cell(cols[0], 6, date_str, 1, 0, "C")
        pdf.cell(cols[1], 6, store_str, 1, 0, "L")
        pdf.cell(cols[2], 6, mat_str, 1, 0, "L")
        pdf.cell(cols[3], 6, val_str, 1, 0, "R")
        pdf.ln()
        total += row["Wartość (PLN)"]

    pdf.set_font("helvetica", "B", 10)
    pdf.cell(sum(cols[:3]), 8, "SUMA BRUTTO:", 1, 0, "R")
    pdf.cell(cols[3], 8, f"{total:.2f} PLN", 1, 1, "R")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

# Główna funkcja modułu
def render_expenses_tab():
    init_expenses_db()
    
    st.header("🧾 Rejestr Wydatków i Materiałów")
    st.write("Kontrola kosztów z paragonów i faktur za materiały elektryczne oraz eksport do PDF.")

    with st.expander("📋 Dane zlecenia do raportu PDF", expanded=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            order_title = st.text_input("Nazwa zlecenia / Obiekt", value="Instalacja elektryczna - dom jednorodzinny")
            contractor = st.text_input("Wykonawca (Serwis / Firma)", value="Automatyka i Technika Napedow")
        with col_p2:
            investor = st.text_input("Inwestor (Klient)", value="Damian Falkowski, ul. Kamienna 1, Lubicz Gorny")

    with st.expander("➕ Dodaj nowy zakup (paragon / faktura)", expanded=False):
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                exp_date = st.date_input("Data zakupu", value=datetime.today())
                exp_store = st.selectbox("Sklep / Sprzedawca", ["Leroy Merlin (Torun)", "ASAJ Sp. z o.o.", "Inny"])
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

    stores = ["Wszystkie", "Leroy Merlin (Torun)", "ASAJ Sp. z o.o.", "Inny"]
    selected_store = st.selectbox("Filtruj według sklepu", stores)

    df = get_expenses(selected_store)

    if not df.empty:
        total_cost = df["Wartość (PLN)"].sum()
        
        m1, m2 = st.columns(2)
        m1.metric(label="Łączny koszt materiałów", value=f"{total_cost:.2f} PLN")
        m2.metric(label="Liczba pozycji", value=len(df))

        st.dataframe(df, use_container_width=True, hide_index=True)

        pdf_path = generate_pdf_report(df, contractor, investor, order_title)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Pobierz zestawienie jako PDF",
                data=pdf_file,
                file_name="zestawienie_wydatkow.pdf",
                mime="application/pdf",
            )
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
            
    else:
        st.info("Brak wpisów w bazie dla wybranego filtra.")

if __name__ == "__main__":
    render_expenses_tab()
