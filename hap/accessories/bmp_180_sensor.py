from loguru import logger
from pyhap.accessory import Accessory
from pyhap.const import Category

try:
  from bme280 import bme280

  bme280.bme280_i2c.set_default_i2c_address(0x76)
  bme280.bme280_i2c.set_default_bus(1)
  bme280.setup()
except ImportError:
  logger.warn('Could not import bme280. Substituting fake device.')
  import random

  class bme280:
    # ~25 C is ok to not make the automations start screaming.
    # And RH can be 40%. Meh.
    @staticmethod
    def read_temperature():
      return random.randint(22, 25)

    @staticmethod
    def read_humidity():
      return random.randint(40, 50)


class TemperatureSensor(Accessory):
  category = Category.CATEGORY_SENSOR

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    service = self.add_preload_service('TemperatureSensor')
    self.temperature = service.configure_char('CurrentTemperature')

  @Accessory.run_at_interval(5)
  async def run(self):
    self.temperature.set_value(bme280.read_temperature())


class HumiditySensor(Accessory):
  category = Category.CATEGORY_SENSOR

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    service = self.add_preload_service('HumiditySensor')
    self.humidity = service.configure_char('CurrentRelativeHumidity')

  @Accessory.run_at_interval(5)
  async def run(self):
    self.humidity.set_value(bme280.read_humidity())
