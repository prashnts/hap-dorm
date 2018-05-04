import requests
import logging


from addict import Dict as AttrDict
from pyhap.accessory import AsyncAccessory
from pyhap.const import CATEGORY_LIGHTBULB
from colorutils import Color
from pydash import py_

config = AttrDict()

config.proto.pixel_prefix = 'ld'
config.proto.brightness_prefix = 'brightness'
config.colors = AttrDict({
  'off': '000000',
  'warm_1': 'F74401',
})
config.pixels.count = 45

config.endpoint = 'http://192.168.0.132/'


class LEDStrands(AsyncAccessory):
  category = CATEGORY_LIGHTBULB

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.0',
      manufacturer='noop.pw',
      model='pw.noop.hap.ws2812',
      serial_number='42-AC-WS2812')

    serv_strands = self.add_preload_service('Lightbulb', ['On', 'Hue', 'Saturation', 'Brightness',])

    self.maybe_put_hue = py_.debounce(self.put_hue, 500)

    self.char_state = serv_strands.configure_char('On', setter_callback=self.update_color)
    self.char_hue = serv_strands.configure_char('Hue', setter_callback=self.update_color, value=0)
    self.char_saturation = serv_strands.configure_char('Saturation', setter_callback=self.update_color, value=0)
    self.char_brightness = serv_strands.configure_char('Brightness', setter_callback=self.update_color, value=0)

  def set_state(self, state):
    if state:
      self.put_hue(config.colors.warm_1)
    else:
      self.put_hue(config.colors.off)

  def update_color(self, value):
    h = self.char_hue.value
    s = self.char_saturation.value / 100
    v = self.char_brightness.value / 100 if self.char_state.value else 0

    col = Color(hsv=(h, s, v))
    logging.info(col.hex)
    self.maybe_put_hue(col.hex.strip('#'))

  def _put_pixel_hue(self, pixels):
    headers = {'ld{}'.format(i): c for i, c in pixels}
    requests.put(config.endpoint, headers=headers)

  def _put_brightness(self, value):
    headers = {config.proto.brightness_prefix: str(value)}
    requests.put(config.endpoint, headers=headers)

  def put_hue(self, hue):
    payload = [(i, hue) for i in range(config.pixels.count)]
    self._put_pixel_hue(payload)
