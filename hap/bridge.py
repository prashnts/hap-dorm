import logging

from pyhap.accessory import Bridge

from .accessories import TemperatureSensor, HumiditySensor

logging.basicConfig(level=logging.INFO)

def init_bridge(driver):
  bridge = Bridge(driver, display_name='Krypton Bridge')
  bridge.add_accessory(TemperatureSensor('Temperature'))
  bridge.add_accessory(HumiditySensor('Humidity'))
  bridge.set_info_service(
    firmware_revision='v1.5',
    manufacturer='noop.pw',
    model='pw.noop.hap.bridge',
    serial_number='42-BR-DORM')
  return bridge
