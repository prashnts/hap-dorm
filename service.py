import logging
import signal

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader

from accessories import BMP180Sensor, LEDStrands, TristarFan

logging.basicConfig(level=logging.INFO)


bridge = Bridge(display_name='Dorm HAP Bridge')
bridge.add_accessory(BMP180Sensor('Temperature'))
bridge.add_accessory(LEDStrands('Strands'))
bridge.add_accessory(TristarFan('Fan'))
bridge.set_info_service(
  firmware_revision='v1.5',
  manufacturer='noop.pw',
  model='pw.noop.hap.bridge',
  serial_number='42-BR-DORM')

driver = AccessoryDriver(bridge, port=51826, persist_file='~/.hap-dorm/accessory.state')

signal.signal(signal.SIGINT, driver.signal_handler)
signal.signal(signal.SIGTERM, driver.signal_handler)

if __name__ == '__main__':
  driver.start()
