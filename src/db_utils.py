import os
import time
import shutil
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta


class DWCDatabaseHandler(object):

	def __init__(self, db_filename, max_rows=25000, utc_offset=(-5, 0)):
		"""
		utc_offset is of the form (hours, minutes) to add to UTC 
			time to get local time
		"""
		self.db_filename = db_filename
		self.conn = None
		self.max_rows = max_rows
		self.utc_offset = utc_offset

		self.init_db(db_filename)

	def init_db(self, db_filename):
		try:
			conn = self._create_db_connection(self.db_filename)
			self.conn = conn

			create_sensor_table_sql = self._get_create_sensor_table_sql()
			_ = self._execute_sql(query=create_sensor_table_sql)

		except Error as that_shit:
			if conn:
				conn.close()
			print(that_shit)

	@staticmethod
	def _create_db_connection(db_filename):
		conn = None

		try:
			conn = sqlite3.connect(db_filename)
			return conn

		except Error as that_shit:
			print(f'Error in _create_db_connection: {that_shit}')
			if conn:
				conn.close()
			raise Error

	def close(self):
		if self.conn is not None:
			self.conn.commit()
			self.conn.close()

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

	def _execute_sql(self, query=None, args=(), attempts=0):
		if self.conn is None:
			self.conn = self._create_db_connection(self.db_filename)

		if query is None:
			raise ValueError("No query passed.")

		try:
			cursor = self.conn.cursor()
			cursor.execute(query, args)

			self.conn.commit()
		except sqlite3.OperationalError:
			# If DB is locked, wait a second and try again
			if attempts < 3:
				time.sleep(1)
				return self._execute_sql(query=query, args=args, attempts=attempts+1)
				
			raise SystemError('DB is locked, 3 attempts failed.')

		return cursor.fetchall()

	def write(self, timestamp, modality, value):
		sql = 'INSERT INTO dwc_sensor_data(timestamp,modality,value) VALUES(?,?,?)'

		_ = self._execute_sql(query=sql, args=(timestamp, modality, value))

		# Check the DB size and if too large then create archive file and new DB
		db_rows = self.get_db_size()
		if db_rows >= self.max_rows:
			self.archive_db_file()

	def write_all_to_db(self, voltage, gallons, temp, ph, ec):
		timestamp = time.time()

		# modality 0 = voltage, 1 = gallons, 2 = temperature, 3 = ph, 4 = ec
		for modality, value in enumerate((voltage, gallons, temp, ph, ec)):
			self.write(timestamp, modality, value)

	def _delete_last_n(self, n=1000000):
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
		self._delete_last_n(self.get_db_size() - 10)
