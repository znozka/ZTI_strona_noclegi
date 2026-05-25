import streamlit as st
from sqlalchemy import text

st.title("Wdrażanie Triggerów InnSight")

try:
    conn = st.connection("azure_sql", type="sql")
    st.write("Połączono z Azure SQL. Instaluję automatyzację w bazie danych...")
except Exception as e:
    st.error(f"Błąd połączenia: {e}")
    st.stop()

# Każdy trigger zdefiniowany jako osobny, czysty ciąg tekstowy bez zbędnych komentarzy na początku
trigger_rezerwacje = """
CREATE OR ALTER TRIGGER TR_Rezerwacje_BlokadaTerminu
ON rezerwacje
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM inserted WHERE status = 'potwierdzona')
    BEGIN
        WITH DatyRezerwacji AS (
            SELECT i.id_noclegu, i.data_zameldowania as DataRez, i.data_wymeldowania
            FROM inserted i WHERE i.status = 'potwierdzona'
            UNION ALL
            SELECT id_noclegu, DATEADD(day, 1, DataRez), data_wymeldowania
            FROM DatyRezerwacji
            WHERE DATEADD(day, 1, DataRez) < data_wymeldowania
        )
        MERGE kalendarz_dostepnosci AS target
        USING DatyRezerwacji AS source
        ON (target.id_noclegu = source.id_noclegu AND target.data = source.DataRez)
        WHEN MATCHED THEN
            UPDATE SET czy_dostepny = 0
        WHEN NOT MATCHED THEN
            INSERT (id_noclegu, data, czy_dostepny)
            VALUES (source.id_noclegu, source.DataRez, 0);
    END
END
"""

trigger_opinie = """
CREATE OR ALTER TRIGGER TR_Opinie_PrzeliczAgregaty
ON opinie
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @NoclegiDoAktualizacji TABLE (id_noclegu INT);

    INSERT INTO @NoclegiDoAktualizacji
    SELECT id_noclegu FROM inserted
    UNION
    SELECT id_noclegu FROM deleted;

    UPDATE n
    SET 
        n.srednia_ocena = ISNULL(o.Srednia, 0.00),
        n.liczba_opinii = ISNULL(o.Ilosc, 0)
    FROM noclegi n
    LEFT JOIN (
        SELECT id_noclegu, AVG(CAST(ocena AS DECIMAL(3,2))) as Srednia, COUNT(id_opinii) as Ilosc
        FROM opinie
        GROUP BY id_noclegu
    ) o ON n.id_noclegu = o.id_noclegu
    WHERE n.id_noclegu IN (SELECT id_noclegu FROM @NoclegiDoAktualizacji);
END
"""

trigger_historia = """
CREATE OR ALTER TRIGGER TR_Opinie_HistoriaEdycji
ON opinie
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(ocena) OR UPDATE(komentarz)
    BEGIN
        INSERT INTO historia_opinii (id_opinii, stara_ocena, stary_komentarz)
        SELECT d.id_opinii, d.ocena, d.komentarz
        FROM deleted d
        JOIN inserted i ON d.id_opinii = i.id_opinii;

        UPDATE o
        SET o.czy_edytowana = 1, o.data_modyfikacji = GETDATE()
        FROM opinie o
        JOIN inserted i ON o.id_opinii = i.id_opinii;
    END
END
"""

with conn.session as session:
    try:
        # Wykonujemy każdy trigger w osobnym wywołaniu sesji, eliminując konflikty składniowe
        session.execute(text(trigger_rezerwacje.strip()))
        session.execute(text(trigger_opinie.strip()))
        session.execute(text(trigger_historia.strip()))
        
        session.commit()
        st.success("Sukces! Wszystkie triggery zostały pomyślnie utworzone bezpośrednio w Azure SQL!")
        st.balloons()
    except Exception as e:
        session.rollback()
        st.error(f"Blad podczas tworzenia triggerów: {e}")