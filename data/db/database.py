from zoneinfo import ZoneInfo
from datetime import datetime
import sqlite3
import logging
import time

TIME_FMT = "%Y-%m-%d %H:%M:%S.%f"
TIME_ZONE = "America/New_York"


class DeviceDatabaseHandler:
    def __init__(self, db_filename, wal_mode=True):
        self.db_filename = db_filename
        self.conn = None
        self.wal_mode = wal_mode
        self.init_db()

    def __del__(self):
        self.close()

    def init_db(self):
        self._create_device_data_table()
        self._create_device_errors_table()

    @staticmethod
    def _create_db_connection(db_filename, wal_mode=True):
        conn = None
        try:
            conn = sqlite3.connect(db_filename)
            if wal_mode:
                conn.execute('pragma journal_mode=wal;')
                conn.commit()
            return conn

        except Exception as e:
            if conn is not None:
                conn.close()
            logging.error(f'Error in _create_db_connection: {e}')
            raise e

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def execute_sql(self, query=None, args=(), attempts=0, catch_errors=True, max_tries=3):
        if query is None:
            self.close()
            raise ValueError("No query passed.")

        if self.conn is None:
            self.conn = self._create_db_connection(db_filename=self.db_filename, 
                                                   wal_mode=self.wal_mode)

        if catch_errors:
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, args)
                self.conn.commit()

            except Exception as e:
                # If DB may be locked, wait a second and try again
                if attempts < max_tries:
                    logging.warning('Exception encountered while attempting to execute SQL. Retrying...')
                    time.sleep(attempts + 1)
                    return self.execute_sql(query=query, args=args, attempts=attempts+1)
                raise e
        else:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            self.conn.commit()

        results = cursor.fetchall()
        self.close()

        return results

    def _create_device_data_table(self):
        table_def = """
            CREATE TABLE IF NOT EXISTS device_data (
                    write_time text PRIMARY KEY,
                    device_name text NOT NULL,
                    value real NOT NULL
            );
            """
        self.execute_sql(query=table_def)
        try:
            self.execute_sql(query="CREATE INDEX device_name_idx ON device_data(device_name);", catch_errors=False)
            self.execute_sql(query="CREATE INDEX value_idx ON device_data(value);", catch_errors=False)
        except sqlite3.OperationalError:
            # Indexes already exist
            pass

    def _create_device_errors_table(self):
        table_def = """
            CREATE TABLE IF NOT EXISTS device_errors (
                    write_time text PRIMARY KEY,
                    device_name text NOT NULL,
                    error_trace text
            );
            """
        self.execute_sql(query=table_def)
        try:
            self.execute_sql(query="CREATE INDEX device_name_idx ON device_data(device_name);", catch_errors=False)
        except sqlite3.OperationalError:
            # Indexes already exist
            pass

    def write_value(self, device_name, device_value):
        write_time = datetime.now(ZoneInfo(TIME_ZONE)).strftime(TIME_FMT)
        query = "INSERT INTO device_data (write_time, device_name, value) VALUES (?,?,?)"
        _ = self.execute_sql(query=query, args=(write_time, device_name, device_value))

    def write_error(self, device_name, error_trace):
        write_time = datetime.now(ZoneInfo(TIME_ZONE)).strftime(TIME_FMT)
        query = "INSERT INTO device_errors (write_time, device_name, error_trace) VALUES (?,?,?)"
        _ = self.execute_sql(query=query, args=(write_time, device_name, error_trace))

    def read_device_latest(self, device_name):
        query = """SELECT DISTINCT write_time, device_name, value 
                   FROM device_data 
                   WHERE device_name = ? 
                   AND write_time = (SELECT MAX(write_time) 
                                     FROM device_data 
                                     WHERE device_name = ?)
                   """
        return self.execute_sql(query=query, args=(device_name, device_name))

    def read_device_since(self, device_name, since):
        query = """SELECT DISTINCT write_time, device_name, value 
                   FROM device_data 
                   WHERE device_name = ? 
                   AND write_time >= ?
                   ORDER BY 1
                   """
        return self.execute_sql(query=query, args=(device_name, since))

    def read_all_latest(self):
        query = """
                WITH latest_times AS (
                    SELECT device_name, MAX(write_time) AS last_write_time
                    FROM device_data
                    GROUP BY 1
                )

                SELECT DISTINCT device_data.write_time, device_data.device_name, device_data.value
                FROM device_data
                JOIN latest_times
                ON device_data.device_name = latest_times.device_name
                AND device_data.write_time = latest_times.last_write_time
                ORDER BY 1
                """
        return self.execute_sql(query=query)

    def read_all_since(self, since):
        query = """
                SELECT DISTINCT write_time, device_name, value
                FROM device_data
                WHERE write_time >= ?
                ORDER BY 1
                """
        return self.execute_sql(query=query, args=(since,))
