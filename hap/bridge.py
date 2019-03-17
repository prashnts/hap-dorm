import logging

from pyhap.accessory import Bridge

from .accessories import BMP180Sensor, LEDStrands, TristarFan, ARPOccupancySensor

logging.basicConfig(level=logging.INFO)


bridge = Bridge(display_name='Krypton Bridge')
bridge.add_accessory(BMP180Sensor('Temperature'))
# bridge.add_accessory(LEDStrands('Strands'))
# bridge.add_accessory(TristarFan('Fan'))
# bridge.add_accessory(ARPOccupancySensor('Festus'))
bridge.set_info_service(
  firmware_revision='v1.5',
  manufacturer='noop.pw',
  model='pw.noop.hap.bridge',
  serial_number='42-BR-DORM')
