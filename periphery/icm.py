import time
import struct
import spidev
import wiringpi

"""
Originally authored over at https://github.com/pimoroni/icm20948-python

Converted for use with the SPI interface by Erki Meinberg.
"""

CHIP_ID = 0xEA
I2C_ADDR = 0x68
I2C_ADDR_ALT = 0x69
ICM20948_BANK_SEL = 0x7f

ICM20948_I2C_MST_ODR_CONFIG = 0x00
ICM20948_I2C_MST_CTRL = 0x01
ICM20948_I2C_MST_DELAY_CTRL = 0x02
ICM20948_I2C_SLV0_ADDR = 0x03
ICM20948_I2C_SLV0_REG = 0x04
ICM20948_I2C_SLV0_CTRL = 0x05
ICM20948_I2C_SLV0_DO = 0x06
ICM20948_EXT_SLV_SENS_DATA_00 = 0x3B

ICM20948_GYRO_SMPLRT_DIV = 0x00
ICM20948_GYRO_CONFIG_1 = 0x01
ICM20948_GYRO_CONFIG_2 = 0x02

# Bank 0
ICM20948_WHO_AM_I = 0x00
ICM20948_USER_CTRL = 0x03
ICM20948_PWR_MGMT_1 = 0x06
ICM20948_PWR_MGMT_2 = 0x07
ICM20948_INT_PIN_CFG = 0x0F

ICM20948_ACCEL_SMPLRT_DIV_1 = 0x10
ICM20948_ACCEL_SMPLRT_DIV_2 = 0x11
ICM20948_ACCEL_INTEL_CTRL = 0x12
ICM20948_ACCEL_WOM_THR = 0x13
ICM20948_ACCEL_CONFIG = 0x14
ICM20948_ACCEL_XOUT_H = 0x2D
ICM20948_GRYO_XOUT_H = 0x33

AK09916_I2C_ADDR = 0x0c
AK09916_CHIP_ID = 0x09
AK09916_WIA = 0x01
AK09916_ST1 = 0x10
AK09916_ST1_DOR = 0b00000010   # Data overflow bit
AK09916_ST1_DRDY = 0b00000001  # Data self.ready bit
AK09916_HXL = 0x11
AK09916_ST2 = 0x18
AK09916_ST2_HOFL = 0b00001000  # Magnetic sensor overflow bit
AK09916_CNTL2 = 0x31
AK09916_CNTL2_MODE = 0b00001111
AK09916_CNTL2_MODE_OFF = 0
AK09916_CNTL2_MODE_SINGLE = 1
AK09916_CNTL2_MODE_CONT1 = 2
AK09916_CNTL2_MODE_CONT2 = 4
AK09916_CNTL2_MODE_CONT3 = 6
AK09916_CNTL2_MODE_CONT4 = 8
AK09916_CNTL2_MODE_TEST = 16
AK09916_CNTL3 = 0x32


class ICM20948:
	def write(self, reg, value):
		"""Write byte to the sensor."""
		wiringpi.digitalWrite(self._cs, 0)

		addr = reg

		data = [addr, value]

		self._bus.writebytes(data)
		time.sleep(0.001)

		wiringpi.digitalWrite(self._cs, 1)

	def read(self, reg):
		"""Read byte from the sensor."""

		wiringpi.digitalWrite(self._cs, 0)

		addr = 0x80 | reg
		self._bus.writebytes([addr])

		ret = self._bus.readbytes(1)
		time.sleep(0.001)

		wiringpi.digitalWrite(self._cs, 1)

		return ret[0]

	def read_bytes(self, reg, length=1):
		"""Read byte(s) from the sensor."""

		wiringpi.digitalWrite(self._cs, 0)

		addr = 0x80 | reg
		self._bus.writebytes([addr])

		ret = self._bus.readbytes(length)
		time.sleep(0.001)

		wiringpi.digitalWrite(self._cs, 1)

		return ret

	def bank(self, value):
		"""Switch register self.bank."""
		if not self._bank == value:
			self.write(ICM20948_BANK_SEL, value << 4)
			self._bank = value

	def mag_write(self, reg, value):
		"""Write a byte to the slave magnetometer."""
		self.bank(3)
		self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR)  # Write one byte
		self.write(ICM20948_I2C_SLV0_REG, reg)
		self.write(ICM20948_I2C_SLV0_DO, value)
		self.bank(0)

	def mag_read(self, reg):
		"""Read a byte from the slave magnetometer."""
		self.bank(3)
		self.write(ICM20948_I2C_SLV0_CTRL, 0x80 | 1)  # Read 1 byte
		self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR | 0x80)
		self.write(ICM20948_I2C_SLV0_REG, reg)
		self.write(ICM20948_I2C_SLV0_DO, 0xff)
		self.bank(0)
		return self.read(ICM20948_EXT_SLV_SENS_DATA_00)

	def mag_read_bytes(self, reg, length=1):
		"""Read up to 24 bytes from the slave magnetometer."""
		self.bank(3)
		self.write(ICM20948_I2C_SLV0_CTRL, 0x80 | 0x08 | length)
		self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR | 0x80)
		self.write(ICM20948_I2C_SLV0_REG, reg)
		self.write(ICM20948_I2C_SLV0_DO, 0xff)
		self.bank(0)
		return self.read_bytes(ICM20948_EXT_SLV_SENS_DATA_00, length)

	def magnetometer_ready(self):
		"""Check the magnetometer status self.ready bit."""
		return self.mag_read(AK09916_ST1) & 0x01 > 0

	def read_magnetometer_data(self):
		self.mag_write(AK09916_CNTL2, 0x01)  # Trigger single measurement
		while not self.magnetometer_ready():
			time.sleep(0.00001)

		data = self.mag_read_bytes(AK09916_HXL, 6)

		# Read ST2 to confirm self.read finished,
		# needed for continuous modes
		# self.mag_read(AK09916_ST2)

		x, y, z = struct.unpack("<hhh", bytearray(data))

		# Scale for magnetic flux density "uT"
		# from section 3.3 of the datasheet
		# This value is constant
		x *= 0.15
		y *= 0.15
		z *= 0.15

		return x, y, z

	def read_accelerometer_gyro_data(self):
		self.bank(0)
		data = self.read_bytes(ICM20948_ACCEL_XOUT_H, 12)

		ax, ay, az, gx, gy, gz = struct.unpack(">hhhhhh", bytearray(data))

		self.bank(2)

		# Read accelerometer full scale range and
		# use it to compensate the self.reading to gs
		scale = (self.read(ICM20948_ACCEL_CONFIG) & 0x06) >> 1

		# scale ranges from section 3.2 of the datasheet
		gs = [16384.0, 8192.0, 4096.0, 2048.0][scale]

		ax /= gs
		ay /= gs
		az /= gs

		# Read back the degrees per second rate and
		# use it to compensate the self.reading to dps
		scale = (self.read(ICM20948_GYRO_CONFIG_1) & 0x06) >> 1

		# scale ranges from section 3.1 of the datasheet
		dps = [131, 65.5, 32.8, 16.4][scale]

		gx /= dps
		gy /= dps
		gz /= dps

		return ax, ay, az, gx, gy, gz

	def set_accelerometer_sample_rate(self, rate=125):
		"""Set the accelerometer sample rate in Hz."""
		self.bank(2)
		# 125Hz - 1.125 kHz / (1 + rate)
		rate = int((1125.0 / rate) - 1)
		# TODO maybe use struct to pack and then write_bytes
		self.write(ICM20948_ACCEL_SMPLRT_DIV_1, (rate >> 8) & 0xff)
		self.write(ICM20948_ACCEL_SMPLRT_DIV_2, rate & 0xff)

	def set_accelerometer_full_scale(self, scale=16):
		"""Set the accelerometer fulls cale range to +- the supplied value."""
		self.bank(2)
		value = self.read(ICM20948_ACCEL_CONFIG) & 0b11111001
		value |= {2: 0b00, 4: 0b01, 8: 0b10, 16: 0b11}[scale] << 1
		self.write(ICM20948_ACCEL_CONFIG, value)

	def set_accelerometer_low_pass(self, enabled=True, mode=5):
		"""Configure the accelerometer low pass filter."""
		self.bank(2)
		value = self.read(ICM20948_ACCEL_CONFIG) & 0b10001110
		if enabled:
			value |= 0b1
		value |= (mode & 0x07) << 4
		self.write(ICM20948_ACCEL_CONFIG, value)

	def set_gyro_sample_rate(self, rate=100):
		"""Set the gyro sample rate in Hz."""
		self.bank(2)
		# 100Hz sample rate - 1.1 kHz / (1 + rate)
		rate = int((1100.0 / rate) - 1)
		self.write(ICM20948_GYRO_SMPLRT_DIV, rate)

	def set_gyro_full_scale(self, scale=250):
		"""Set the gyro full scale range to +- supplied value."""
		self.bank(2)
		value = self.read(ICM20948_GYRO_CONFIG_1) & 0b11111001
		value |= {250: 0b00, 500: 0b01, 1000: 0b10, 2000: 0b11}[scale] << 1
		self.write(ICM20948_GYRO_CONFIG_1, value)

	def set_gyro_low_pass(self, enabled=True, mode=5):
		"""Configure the gyro low pass filter."""
		self.bank(2)
		value = self.read(ICM20948_GYRO_CONFIG_1) & 0b10001110
		if enabled:
			value |= 0b1
		value |= (mode & 0x07) << 4
		self.write(ICM20948_GYRO_CONFIG_1, value)

	def __init__(self, cs=22, init_wiring_pi=False):
		self._bank = -1

		if init_wiring_pi:
			wiringpi.wiringPiSetupGpio()

		self._cs = cs

		wiringpi.pinMode(self._cs, 1)
		wiringpi.digitalWrite(self._cs, 1)

		self._bus = spidev.SpiDev()
		self._bus.open(0, 1)
		self._bus.max_speed_hz = 500000
		self._bus.mode = 3

		self.bank(0)
		if not self.read(ICM20948_WHO_AM_I) == CHIP_ID:
			raise RuntimeError("Unable to find ICM20948")

		self.write(ICM20948_PWR_MGMT_1, 0x01)
		self.write(ICM20948_PWR_MGMT_2, 0x00)

		self.bank(2)

		self.set_gyro_sample_rate(100)
		self.set_gyro_low_pass(enabled=True, mode=5)
		self.set_gyro_full_scale(250)

		self.set_accelerometer_sample_rate(125)
		self.set_accelerometer_low_pass(enabled=True, mode=5)
		self.set_accelerometer_full_scale(16)

		self.bank(0)
		self.write(ICM20948_INT_PIN_CFG, 0x30)
		self.write(ICM20948_USER_CTRL, 0x20)

		self.bank(3)
		self.write(ICM20948_I2C_MST_CTRL, 0x4D)
		self.write(ICM20948_I2C_MST_DELAY_CTRL, 0x01)
		self.write(0x05, 0x81)

		if not self.mag_read(AK09916_WIA) == AK09916_CHIP_ID:
                        time.sleep(1)
                        return self.__init__(cs, init_wiring_pi)
			#raise RuntimeError("Unable to find AK09916")

		# Reset the magnetometer
		self.mag_write(AK09916_CNTL3, 0x01)
		while self.mag_read(AK09916_CNTL3) == 0x01:
			time.sleep(0.0001)

		time.sleep(1)
		self.mag_write(0x31, 0x02);
