def get_available_rooms(conn, date_start, date_end):
    query = "SELECT * FROM Pokoje WHERE id NOT IN (...)"
    return conn.query(query)
