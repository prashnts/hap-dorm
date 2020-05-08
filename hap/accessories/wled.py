import requests
import logging


from addict import Dict as AttrDict
from pyhap.accessory import AsyncAccessory
from pyhap import const
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
  category = const.CATEGORY_LIGHTBULB

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.0',
      manufacturer='noop.pw',
      model='pw.noop.hap.ws2812',
      serial_number='42-AC-WS2812')

    strands = self.add_preload_service('Lightbulb', chars=[
      'On',
      'Hue',
      'Saturation',
      'Brightness',
    ])

    self.props = AttrDict(
      active=strands.configure_char('On', setter_callback=self.set_prop('active')),
      hue=strands.configure_char('Hue', setter_callback=self.set_prop('hue')),
      saturation=strands.configure_char('Saturation', setter_callback=self.set_prop('saturation')),
      brightness=strands.configure_char('Brightness', setter_callback=self.set_prop('brightness')))

    self.state = AttrDict(
      changed=True,
      hue=0,
      saturation=0,
      brightness=0,
      active=0)

  def set_prop(self, prop):
    def update_prop(value, prop=prop):
      self.state.changed = True
      setattr(self.state, prop, value)
    return update_prop

  def set_state(self, state):
    if state:
      self.put_hue(config.colors.warm_1)
    else:
      self.put_hue(config.colors.off)

  def update_color(self):
    h = self.state.hue
    s = self.state.saturation / 100
    v = self.state.brightness / 100 if self.state.active else 0

    col = Color(hsv=(h, s, v))
    logging.info(col.hex)
    self.put_hue(col.hex.strip('#'))

  def _put_pixel_hue(self, pixels):
    headers = {'ld{}'.format(i): c for i, c in pixels}
    requests.put(config.endpoint, headers=headers)

  def put_hue(self, hue):
    payload = [(i, hue) for i in range(config.pixels.count)]
    self._put_pixel_hue(payload)

  @AsyncAccessory.run_at_interval(4)
  async def run(self):
    logging.info(str(self.state))
    if self.state.changed:
      self.state.changed = False
      self.update_color()
