import serial
import time

Usart_timeout = 0.005

class PiBot:
	battery = 0
	encoder =	[None] * 2
	imu 	= 	[None] * 7
	sensor 	= 	[None] * 16
	
	MCU_UART = serial.Serial(
		port='/dev/serial0',
		baudrate = 115200,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS,
		timeout=Usart_timeout
	)
	
	def _pi_usart_flush(self):
		self.MCU_UART.timeout = 0.0001
		while not self.MCU_UART.read(1):
			self.MCU_UART.write(b'Y')
		while self.MCU_UART.read(1):
			pass
		self.MCU_UART.timeout = Usart_timeout
		
	def _adc_conf(self, conf = 3):
		self._pi_usart_flush()
		self.MCU_UART.write(b'x:%04d' % conf)
		if self.MCU_UART.read(6) == (b'x:%04d' % conf):
			val = self.MCU_UART.read(3)
			if val == (b'%03d' % conf):
				return True

		return False
			
	def _adc_read(self, conf = 3):
		i=0
		self._pi_usart_flush()
		self.MCU_UART.timeout = 0.02
		self.MCU_UART.write(b'a:%04d' % conf)
		if self.MCU_UART.read(6) == b'a:%04d' % conf:
			if	conf == 3:
				val = self.MCU_UART.read(80)
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
				self.MCU_UART.timeout = Usart_timeout
				return True
			elif conf == 2 or conf == 1:
				val = self.MCU_UART.read(40)
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
				self.MCU_UART.timeout = Usart_timeout
				return True
			else: 
				val = self.MCU_UART.read(6)
				print('read nothing')
				
		self.MCU_UART.timeout = Usart_timeout
		return False
	
	def _buzzer_set(self, buzzer):
		self._pi_usart_flush()
		self.MCU_UART.write(b'g:%04d' % buzzer)
		if self.MCU_UART.read(6) == b'g:%04d' % buzzer:
			val = self.MCU_UART.read(6)
			if val == (b'buzzer'):
				return True
		return False
	
	def _battery_read(self):
		self._pi_usart_flush()
		self.MCU_UART.write(b'b:0000')
		if self.MCU_UART.read(6) == b'b:0000':
			val = self.MCU_UART.read(4)
			if val != b'':
				self.battery = int(val.decode('ascii'))
		return False
		
	def _encoders_enable(self):
		self._pi_usart_flush()
		self.MCU_UART.write(b't:0000')
		if self.MCU_UART.read(6) ==(b't:0000'):
			val = self.MCU_UART.read(4)
			if val == (b'EncE'):
				return True

		return False
		
	def _encoders_get(self):
		self._pi_usart_flush()
		self.MCU_UART.write(b'h:0000')
		if self.MCU_UART.read(6) ==(b'h:0000'):
			val = self.MCU_UART.read(23)
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
		self.MCU_UART.write(b'm:0000')
		if self.MCU_UART.read(6) == (b'm:0000'):
			val = self.MCU_UART.read(6)
			if val == (b'motorE'):
				return True
		return False
		
	def _motorR_set(self, val= 0):
		self._pi_usart_flush()
		self.MCU_UART.write(b'c:%04d' % val)
		if self.MCU_UART.read(6) == (b'c:%04d' % val):
			val = self.MCU_UART.read(6)
			if val == (b'motorR'):
				return True
		return False
			
	def _motorL_set(self, val = 0):
		self._pi_usart_flush()
		self.MCU_UART.write(b'd:%04d' % val)
		if self.MCU_UART.read(6) == (b'd:%04d' % val):
			val = self.MCU_UART.read(6)
			if val == (b'motorL'):
				return True
		return False
		
	def _motorB_set(self, val = 0):
		self._pi_usart_flush()
		self.MCU_UART.write(b'l:%04d' % val)
		if self.MCU_UART.read(6) == (b'l:%04d' % val):
			val = self.MCU_UART.read(6)
			if val == (b'motorB'):
				return True
		return False
		
	def _servo_enable(self):
		self._pi_usart_flush()
		self.MCU_UART.write(b's:0000')
		if self.MCU_UART.read(6) == (b's:0000'):
			val = self.MCU_UART.read(6)
			if val == (b'servoE'):
				return True
		return False
		
	def _servo_one_set(self, val = 20):
		self._pi_usart_flush()
		self.MCU_UART.write(b'e:%04d' % val)
		if self.MCU_UART.read(6) == (b'e:%04d' % val):
			val = self.MCU_UART.read(6)
			if val == (b'servo1'):
				return True
		return False
			
	def _servo_two_set(self, val = 20):
		self._pi_usart_flush()
		self.MCU_UART.write(b'f:%04d' % val)
		if self.MCU_UART.read(6) == (b'f:%04d' % val):
			val = self.MCU_UART.read(6)
			if val == (b'servo2'):
				return True
		return False
		
	def _imu_enable(self):
		self._pi_usart_flush()
		self.MCU_UART.write(b'j:0000')
		if self.MCU_UART.read(6) == (b'j:0000'):
			time.sleep(0.5)
			val = self.MCU_UART.read(6)
			if val == (b'IMUOK'):
				return True
		return False
		
	def _imu_read(self):
		self._pi_usart_flush()
		self.MCU_UART.timeout = 0.01
		i=0
		self.MCU_UART.write(b'i:0000')
		if self.MCU_UART.read(6) == b'i:0000':
			val = self.MCU_UART.read(56)
			val = val.decode('ascii')
			val = val.split(',')
			for x in val:
				if x == '':
					break
				try:
					self.imu[i] = int(x)
				except:
					pass
				i+=1
			return True 
		self.MCU_UART.timeout = Usart_timeout
		return False
