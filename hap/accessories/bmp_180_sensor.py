from pyhap.accessory import AsyncAccessory
from pyhap.const import CATEGORY_SENSOR

from bme280 import bme280

bme280.bme280_i2c.set_default_i2c_address(0x76)
bme280.bme280_i2c.set_default_bus(1)
bme280.setup()


class TemperatureSensor(AsyncAccessory):
  category = CATEGORY_SENSOR

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.2',
      manufacturer='noop.pw',
      model='pw.noop.hap.sense-temp',
      serial_number='42-AC-S-TEMP')

    service = self.add_preload_service('TemperatureSensor')
    self.temperature = service.configure_char('CurrentTemperature')

  @AsyncAccessory.run_at_interval(5)
  async def run(self):
    self.temperature.set_value(bme280.read_temperature())


class HumiditySensor(AsyncAccessory):
  category = CATEGORY_SENSOR

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.2',
      manufacturer='noop.pw',
      model='pw.noop.hap.sense-temp',
      serial_number='42-AC-S-TEMP')

    service = self.add_preload_service('HumiditySensor')
    self.humidity = service.configure_char('CurrentRelativeHumidity')

  @AsyncAccessory.run_at_interval(5)
  async def run(self):
    self.humidity.set_value(bme280.read_humidity())
