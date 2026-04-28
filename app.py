import streamlit as st

# Inicjalizacja połączenia przy użyciu danych z secrets.toml
conn = st.connection("azure_sql", type="sql")

st.title("Moja Aplikacja z Azure SQL")

# odczyt danych
st.subheader("Dane z bazy")
query = "SELECT * FROM SalesLT.Address"
df = conn.query(query, ttl=600) # ttl to cache na 10 minut
st.dataframe(df)

# zapis danych
st.subheader("Dodaj nowy wpis")
with st.form("insert_form"):
    nowe_imie = st.text_input("Imię")
    submit = st.form_submit_button("Wyślij")
    
    if submit:
        with conn.session as session:
            # używamy parametrów, aby uniknąć SQL Injection!
            session.execute(
                "INSERT INTO TwojaTabela (imie) VALUES (:name);",
                {"name": nowe_imie}
            )
            session.commit()
        st.success("Dodano do bazy!")
        st.rerun() # odśwież, by zobaczyć zmiany
