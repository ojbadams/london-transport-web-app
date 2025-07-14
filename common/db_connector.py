import psycopg


class PostgresConnector:
    def __init__(self, host, dbname, user, password, port=5432):
        self.connection_params = {
            "host": host,
            "dbname": dbname,
            "user": user,
            "password": password,
            "port": port,
        }
        self.conn = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg.connect(**self.connection_params)
        return self.conn

    def execute_query(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params)
            try:
                result = cur.fetchall()
            except psycopg.ProgrammingError:
                # No results to fetch (e.g., for INSERT/UPDATE)
                result = None
        conn.commit()
        return result

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None
