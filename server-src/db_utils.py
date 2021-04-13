import sqlite3
from sqlite3 import Error, DatabaseError


class DWCServerDatabaseHandler(object):

	def __init__(self, db_filename):
		self.db_filename = db_filename
		self.conn = None
		self.init_db()

	def __del__(self):
		self.close()

	def init_db(self, db_filename):
		conn = self._create_db_connection(self.db_filename)
		self.conn = conn

		create_sensor_table_sql = self._get_create_sensor_table_sql()
		_ = self._execute_sql(query=create_sensor_table_sql)

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
			self.conn.close()

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

	def _read_latest_modality(self, modality, attempts=1):
		query = f"""SELECT timestamp, value 
			   	    FROM dwc_sensor_data 
				    WHERE modality={modality} 
				    AND timestamp=(
				    	SELECT MAX(timestamp) 
				    	FROM dwc_sensor_data 
				    	WHERE modality={modality}
				    )"""

		# Returns a list containing one tuple of the form (timestamp,  value)
		row = self._execute_sql(query=query)

		if row:
			return row[0][1]
		return None

	def _read_modalities_since(self, modalities, since, attempts=1):
		query = f"""SELECT timestamp, modality, value 
						   FROM dwc_sensor_data 
						   WHERE modality IN {modalities} 
						   AND timestamp>={since}"""

		# Returns a list containing one tuple of the form (timestamp,  value)
		return self._execute_sql(query=query)

	@staticmethod
	def get_modality_map():
		# modality 0 = voltage, 1 = gallons, 2 = temperature, 3 = pH, 4 = PPM
		return {0: 'Gallons in reservoir',
				1: 'Reservoir pH',
				2: 'Reservoir PPM',
				3: 'Reservoir temperature'}

	def read_latest(self, modalities=(0, 1, 2, 3)):
		if isinstance(modalities, int):
			modalities = (modalities, )
		
		query = f"""
				SELECT timestamp, modality, value
				FROM dwc_sensor_data
				WHERE (modality, timestamp) in

				(
				  SELECT modality, max(timestamp) 
				  FROM dwc_sensor_data
				  WHERE modality IN ({','.join(modalities)})
				  GROUP BY modality
				)
				"""

		results = self._execute_sql(query)
		db_values = {modality: value for _, modality, value in results}

		return db_values

	def read_since(self, since, modalities=(0, 1, 2, 3, 4)):
		modality_map = self.get_modality_map()
		db_values = {str(m): [] for m in modalities}
		db_values['modalities'] = {str(m): modality_map[m] for m in modalities}

		rows = self._read_modalities_since(modalities, since)

		for t, modality, value in rows:
			db_values[str(modality)].append((t, value))

		return db_values

