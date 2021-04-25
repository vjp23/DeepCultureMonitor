import time
import sqlite3
from datetime import datetime, timedelta


class DWCDatabaseHandler(object):

    def __init__(self, db_filename, utc_offset=(-5, 0)):
        """
        utc_offset is of the form (hours, minutes) to add to UTC 
            time to get local time
        """
        self.db_filename = db_filename
        self.conn = None
        self.utc_offset = utc_offset

        self.init_db(db_filename)


    def __del__(self):
        self.close()

    def init_db(self, db_filename):
        conn = self._create_db_connection(self.db_filename)
        self.conn = conn

        create_sensor_table_sql = self._get_create_sensor_table_sql()
        _ = self._execute_sql(query=create_sensor_table_sql)

        create_action_table_sql = self._get_create_action_table_sql()
        _ = self._execute_sql(query=create_action_table_sql)

    @staticmethod
    def _create_db_connection(db_filename):
        conn = None
        try:
            conn = sqlite3.connect(db_filename)
            return conn

        except Exception as e:
            if conn:
                conn.close()
            print(f'Error in _create_db_connection: {e}')
            raise e

    def close(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    @staticmethod
    def _get_create_sensor_table_sql():
        sensor_table_def = """
            CREATE TABLE IF NOT EXISTS dwc_sensor_data (
                    point_id integer PRIMARY KEY,
                    timestamp text NOT NULL,
                    modality integer NOT NULL,
                    value float NOT NULL
            )
            """
        return sensor_table_def

    @staticmethod
    def _get_create_action_table_sql():
        sensor_table_def = """
            CREATE TABLE IF NOT EXISTS dwc_action_data (
                    point_id integer PRIMARY KEY,
                    timestamp text NOT NULL,
                    action integer NOT NULL,
                    value_1 float DEFAULT 0.0,
                    value_2 float DEFAULT 0.0,
                    value_3 float DEFAULT 0.0
            )
            """
        return sensor_table_def

    def _execute_sql(self, query=None, args=(), attempts=0):
        if self.conn is None:
            self.conn = self._create_db_connection(self.db_filename)

        if query is None:
            self.close()
            raise ValueError("No query passed.")

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)

            self.conn.commit()

        except Exception as e:
            # If DB is locked, wait a second and try again
            if attempts < 3:
                time.sleep(1)
                return self._execute_sql(query=query, args=args, attempts=attempts+1)

            raise e

        results = cursor.fetchall()
        self.close()

        return results

    def get_latest(self, modalities=(0, 1, 2, 3)):
        if isinstance(modalities, int):
            modalities = (modalities, )
        
        query = f"""
                SELECT timestamp, modality, value
                FROM dwc_sensor_data
                WHERE (modality, timestamp) in

                (
                  SELECT modality, max(timestamp) 
                  FROM dwc_sensor_data
                  WHERE modality IN ({','.join([str(m) for m in modalities])})
                  GROUP BY modality
                )
                """

        results = self._execute_sql(query)
        db_values = {modality: value for _, modality, value in results}

        return db_values

    def write_one(self, modality, value, timestamp):
        sql = 'INSERT INTO dwc_sensor_data(timestamp,modality,value) VALUES(?,?,?)'

        _ = self._execute_sql(query=sql, args=(timestamp, modality, value))

        # Check the DB size and if too large then create archive file and new DB
        # db_rows = self.get_db_size()
        # if db_rows >= self.max_rows:
        #   self.archive_db_file()

    def write_action(self, action, timestamp, values=()):
        """ 
        values should be a *list* of len 1, 2, or 3 where values are inserted into the value_1, 
        value_2, and value_3 columns respectively. If fewer than 3 values are passed, then
        the columns are filled left to right. For example, if len(values) = 1, then the value will
        be inserted into value_1. If len(values) = 2, then values[0] will be inserted into
        value_1 and values[1] into value_2.

        Action numbers:
        0 = fill tank start, value_1 is starting water level
        1 = fill tank stop, value_1 in ending water level
        """
        if values:
            if len(values) == 1:
                sql = 'INSERT INTO dwc_action_data(timestamp,action,value_1) VALUES(?,?,?)'
            elif len(values) == 2:
                sql = 'INSERT INTO dwc_action_data(timestamp,action,value_1,value_2) VALUES(?,?,?,?)'
            elif len(values) == 3:
                sql = 'INSERT INTO dwc_action_data(timestamp,action,value_1,value_2,value_3) VALUES(?,?,?,?,?)'
            else:
                print('WARNING: TOO MANY VALUES INSERTED INTO THE ACTIONS TABLE. Insert at most 3 values.')
                return
        else:
            sql = 'INSERT INTO dwc_action_data(timestamp,action) VALUES(?,?)'

        _ = self._execute_sql(query=sql, args=(timestamp, action, *values))


    def write_all_to_db(self, gallons, ph, ec, temp):
        timestamp = time.time()

        # modality 0 = gallons, 1 = ph, 2 = ec, 3 = temp
        for modality, value in enumerate((gallons, ph, ec, temp)):
            self.write_one(timestamp, modality, value)

    def _delete_oldeset_n(self, n=1000000):
        sql = f"""DELETE FROM dwc_sensor_data WHERE
            point_id IN (
                SELECT point_id
                FROM dwc_sensor_data
                ORDER BY point_id DESC
                LIMIT {n}
            )"""

        _ = self._execute_sql(query=sql)

    def get_db_size(self):
        sql = "SELECT COUNT(*) FROM dwc_sensor_data"

        # Returns a list of tuples of the form [(num_rows,)]
        row_count = self._execute_sql(query=sql)

        return row_count[0][0]

    def archive_db_file(self):
        # Commit pending DB transactions
        self.conn.commit()

        # Backup the DB file to a new file with the local datetime
        local_time = datetime.now() + timedelta(hours=self.utc_offset[0], 
                                                minutes=self.utc_offset[1])
        db_prefix = self.db_filename[:self.db_filename.index('.db')]
        archive_name = local_time.strftime(f'{db_prefix}_%Y%m%d_%H%M.db')
        
        # Perform the DB backup
        print('Backing up database to ' + archive_name + '...')
        bck = sqlite3.connect(archive_name)
        with bck:
            self.conn.backup(bck)
        bck.close()

        # Delete all rows from table *except* for most recent 10 rows
        self._delete_oldest_n(self.get_db_size() - 10)
