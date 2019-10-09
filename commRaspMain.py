import serial
import time
import threading

from VL53L1X2 import VL53L1X
from periphery import icm
import wiringpi

Usart_timeout = 0.005

class PiBot:
	class _TofHolder:
		def __init__(self, id, addr, gpio):
			self.id = id
			self.addr = addr
			self.gpio = gpio

	def __init__(self):
		self._uart = serial.Serial(
			port='/dev/serial0',
			baudrate = 115200,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=Usart_timeout
		)

		self.battery = 0
		self.encoder = [None] * 2
		self.compass = [None] * 3
		self.gyro = [None] * 6
		self.sensor  = [None] * 16
		self.tof_values = [None] * 3 # LEFT, FRONT, RIGHT

		wiringpi.wiringPiSetupGpio()

		self._tof_master = None
		self._tofs = [
			self._TofHolder(11, 0x2a, 19),
			self._TofHolder(12, 0x2b, 13),
			self._TofHolder(13, 0x2c, 26)
		]

		self._imu = icm.ICM20948()

		self._rotation_z = 0.0
		self._gyro_thread = None
		self._gyro_running = False
		self._gyro_lock = threading.Lock()

	def __del__(self):
		if self._tof_master:
			for holder in self._tofs:
				self._tof_master.stop_ranging(holder.id)

			self._tof_master.close()

	def _gyro_stop(self):
		"""
		Stops the gyro summarizer thread if it is running.
		"""

		if self._gyro_running:
			self._gyro_running = False
			self._gyro_thread.join()

	def _gyro_start(self):
		"""
		Starts the gyro summarizer thread.
		"""

		if not self._gyro_running:
			self._rotation_z = 0.0
			self._gyro_running = True
			self._gyro_thread = threading.Thread(target=self._gyro_worker)

	def _gyro_worker(self):
		"""
		Gyro summarizer. Polls the gyro regularly (usually every 5 ms or so)
		and summarizers the change in rotation into the self._rotation_z variable.

		Because of the GIL, the variables in question should be atomic enough
		to use.
		"""
		current_time_millis = lambda: int(round(time.time() * 1000))
		last_poll = current_time_millis()

		while self._gyro_running:
			time.sleep(0.001)

			self._imu_read_gyro()

			time_now = current_time_millis()
			delta = time_now - last_poll

			if delta < 1:
				continue

			last_poll = time_now
			delta = self._gyro[5] * delta * 1000

			if -0.1 < delta < 0.1:
				continue

			self._rotation_z += delta

	def _tof_init(self) -> bool:
		"""
		Initializes the time of flight sensors of the robot. Absolutely required
		before using them.

		Causes undefined behaviour if one or more ToFs are disconnected.

		Returns True upon success, False otherwise.
		"""

		if self._tof_master:
			return False

		for holder in self._tofs:
			gpio = holder.gpio

			wiringpi.pinMode(gpio, 1)
			wiringpi.digitalWrite(gpio, 0)

		time.sleep(0.2)

		wiringpi.digitalWrite(self._tofs[0].gpio, 1)

		self._tof_master = VL53L1X()
		self._tof_master.open()

		for holder in self._tofs:
			wiringpi.digitalWrite(holder.gpio, 1)
			self._tof_master.add_sensor(holder.id, 0x29)
			self._tof_master.change_address(holder.id, holder.addr)
			self._tof_master.start_ranging(holder.id)

	def _tof_read(self) -> bool:
		"""
		Reads and updates all of the ToF sensor values.

		Returns True upon success, False otherwise.
		"""
		if not self._tof_master:
			return False

		for idx, holder in enumerate(self._tofs):
			self.tof_values[idx] = self._tof_master.get_distance(holder.id)

		return True

	def _pi_usart_flush(self):
		self._uart.timeout = 0.0001
		while not self._uart.read(1):
			self._uart.write(b'Y')
		while self._uart.read(1):
			pass
		self._uart.timeout = Usart_timeout

	def _adc_conf(self, conf = 3):
		self._pi_usart_flush()
		self._uart.write(b'x:%04d' % conf)
		if self._uart.read(6) == (b'x:%04d' % conf):
			val = self._uart.read(3)
			if val == (b'%03d' % conf):
				return True

		return False

	def _sort_raw_adc(self):
		"""
		Sorts ADC values to correspond to the manual.
		"""
		sort_list = [5, 3, 4, 1, 0, 2, 6, 7, 11, 12, 13, 8, 9, 10, 14, 15]

		self.sensor = [self.sensor[i] for i in sort_list]

	def _adc_read(self, conf = 3):
		i=0
		self._pi_usart_flush()
		self._uart.timeout = 0.02
		self._uart.write(b'a:%04d' % conf)
		if self._uart.read(6) == b'a:%04d' % conf:
			if	conf == 3:
				val = self._uart.read(80)
				val = val.decode('ascii')
				val = val.split(',')
				for x in val:
					if x == '':
						break
					try:
						self.sensor[i] = int(x)
					except:
						pass
					i+=1
				self._uart.timeout = Usart_timeout

				self._sort_raw_adc()
				return True
			elif conf == 2 or conf == 1:
				val = self._uart.read(40)
				if conf == 1:
					val = val.decode('ascii')
					val = val.split(',')
					for x in val:
						if x == '':
							break

						try:
							self.sensor[i] = int(x)
						except:
							pass

						i+=1
				elif conf == 2:
					i=8
					val = val.decode('ascii')
					val = val.split(',')
					for x in val:
						if x == '':
							break

						try:
							self.sensor[i] = int(x)
						except:
							pass
						i+=1
				self._uart.timeout = Usart_timeout

				self._sort_raw_adc()
				return True
			else:
				val = self._uart.read(6)
				print('read nothing')

		self._uart.timeout = Usart_timeout
		return False

	def _buzzer_set(self, buzzer):
		self._pi_usart_flush()
		self._uart.write(b'g:%04d' % buzzer)
		if self._uart.read(6) == b'g:%04d' % buzzer:
			val = self._uart.read(6)
			if val == (b'buzzer'):
				return True
		return False

	def _encoders_enable(self):
		self._pi_usart_flush()
		self._uart.write(b't:0000')
		if self._uart.read(6) ==(b't:0000'):
			val = self._uart.read(4)
			if val == (b'EncE'):
				return True

		return False

	def _encoders_get(self):
		self._pi_usart_flush()
		self._uart.write(b'h:0000')
		if self._uart.read(6) ==(b'h:0000'):
			val = self._uart.read(23)
			if val != b'':
				val = (val.decode('ascii')).split(':')
				try:
					self.encoder[0] = val[0]
					self.encoder[1] = val[1]
				except:
					return False
				return True
		return False

	def _motors_enable(self):
		self._pi_usart_flush()
		self._uart.write(b'm:0000')
		if self._uart.read(6) == (b'm:0000'):
			val = self._uart.read(6)
			if val == (b'motorE'):
				return True
		return False

	def _motorR_set(self, val= 0):
		self._pi_usart_flush()
		self._uart.write(b'c:%04d' % val)
		if self._uart.read(6) == (b'c:%04d' % val):
			val = self._uart.read(6)
			if val == (b'motorR'):
				return True
		return False

	def _motorL_set(self, val = 0):
		self._pi_usart_flush()
		self._uart.write(b'd:%04d' % val)
		if self._uart.read(6) == (b'd:%04d' % val):
			val = self._uart.read(6)
			if val == (b'motorL'):
				return True
		return False

	def _motorB_set(self, val = 0):
		self._pi_usart_flush()
		self._uart.write(b'l:%04d' % val)
		if self._uart.read(6) == (b'l:%04d' % val):
			val = self._uart.read(6)
			if val == (b'motorB'):
				return True
		return False

	def _servo_enable(self):
		self._pi_usart_flush()
		self._uart.write(b's:0000')
		if self._uart.read(6) == (b's:0000'):
			val = self._uart.read(6)
			if val == (b'servoE'):
				return True
		return False

	def _servo_one_set(self, val = 20):
		self._pi_usart_flush()
		self._uart.write(b'e:%04d' % val)
		if self._uart.read(6) == (b'e:%04d' % val):
			val = self._uart.read(6)
			if val == (b'servo1'):
				return True
		return False

	def _servo_two_set(self, val = 20):
		self._pi_usart_flush()
		self._uart.write(b'f:%04d' % val)
		if self._uart.read(6) == (b'f:%04d' % val):
			val = self._uart.read(6)
			if val == (b'servo2'):
				return True
		return False

	def _imu_read_compass(self) -> bool:
		"""
		Updates the compass values of the bot. They will be stored under the
		self.compass list.

		The compass has a refresh rate of roughly 30 Hz.

		Returns True upon a successful read.
		"""

		self._gyro_lock.acquire()

		x, y, z = self._imu.read_magnetometer_data()
		self.compass = [x, y, z]

		self._gyro_lock.release()

		return True

	def _imu_read_gyro(self):
		"""
		Updates the accelerometer and gyro values of the bot. They will be stored
		under the self.gyro list.
		"""

		self._gyro_lock.acquire()

		ax, ay, az, gx, gy, gz = self._imu.read_accelerometer_gyro_data()

		self.gyro = [ax, ay, az, gx, gy, gz]

		self._gyro_lock.release()
