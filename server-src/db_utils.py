import sqlite3
from sqlite3 import Error, DatabaseError


class DWCServerDatabaseHandler(object):

    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.conn = None
        self.init_db()

    def init_db(self):
        try:
            self.conn = self._create_db_connection()

        except Error as that_shit:
            if self.conn:
                self.conn.close()
            print(that_shit)

    def _create_db_connection(self):
        conn = None

        try:
            conn = sqlite3.connect(self.db_filename)
            return conn

        except Error as that_shit:
            print(f'Error in _create_db_connection: {that_shit}')
            if conn:
                conn.close()
            raise Error

    def close(self):
        if self.conn is not None:
            self.conn.close()

    def _read_latest_modality(self, modality, attempts=1):
        if attempts >= 3:
            if attempts >= 10:
                raise AttributeError(f'{attempts} DB reads failed.')
            print(f'WARNING: {attempts} DB reads failed. Retrying...')

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"""SELECT timestamp, value 
                              FROM dwc_sensor_data 
                              WHERE modality={modality} 
                              AND timestamp=(SELECT MAX(timestamp) 
                              FROM dwc_sensor_data 
                              WHERE modality={modality})""")

        except DatabaseError as db_error:
            self.close()
            self.init_db()
            return self._read_latest_modality(modality=modality, attempts=attempts+1)

        # Returns a list containing one tuple of the form (timestamp, value)
        row = cursor.fetchall()
        # Get the tuple from the list, then the value from the tuple
        return row[0][1]

    def _read_modalities_since(self, modalities, since, attempts=1):
        if attempts >= 3:
            if attempts >= 10:
                raise AttributeError(f'{attempts} DB reads failed.')
            print(f'WARNING: {attempts} DB reads failed. Retrying...')

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"""SELECT timestamp, modality, value 
                               FROM dwc_sensor_data 
                               WHERE modality IN {modalities} 
                               AND timestamp>={since}""")

        except DatabaseError as db_error:
            self.close()
            self.init_db()
            return self._read_modalities_since(modality=modality, since=since, attempts=attempts+1)

        rows = cursor.fetchall()
        return rows

    @staticmethod
    def get_modality_map():
        # modality 0 = voltage, 1 = gallons, 2 = temperature, 3 = pH, 4 = PPM
        return {0: 'eTape voltage',
                1: 'Gallons to add',
                2: 'Reservoir temperature',
                3: 'Reservoir pH',
                4: 'Reservoir PPM'}

    def read_latest(self, modalities=(0, 1, 2, 3, 4)):
        db_values = dict()

        for modality in modalities:
            db_values[modality] = self._read_latest_modality(modality)

        return db_values

    def read_since(self, since, modalities=(0, 1, 2, 3, 4)):
        modality_map = self.get_modality_map()
        db_values = {str(m): [] for m in modalities}
        db_values['modalities'] = {str(m): modality_map[m] for m in modalities}

        rows = self._read_modalities_since(modalities, since)

        for t, modality, value in rows:
            db_values[str(modality)].append((t, value))

        return db_values

