import Adafruit_BMP.BMP085 as BMP085

from pyhap.accessory import AsyncAccessory
from pyhap.const import CATEGORY_SENSOR


class BMP180Sensor(AsyncAccessory):
  category = CATEGORY_SENSOR

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.2',
      manufacturer='noop.pw',
      model='pw.noop.hap.bmp180',
      serial_number='42-AC-BMP180')

    serv_temperature = self.add_preload_service('TemperatureSensor')
    self.char_temp = serv_temperature.configure_char('CurrentTemperature')

    self.sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

  @AsyncAccessory.run_at_interval(5)
  async def run(self):
    # Offset the temperature by two degrees
    temperature = self.sensor.read_temperature() - 2

    self.char_temp.set_value(temperature)
