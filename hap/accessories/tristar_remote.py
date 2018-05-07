import logging

from addict import Dict as AttrDict
from enum import Enum
from gpiozero import LED as GPIO
from pyhap.accessory import AsyncAccessory
from pyhap.const import CATEGORY_FAN
from time import sleep

from hap import config


gpio_pin = lambda x: GPIO(x, active_high=True, initial_value=True)


class ActiveState(Enum):
  on = 1
  off = 2

  @classmethod
  def from_value(cls, value):
    if value:
      return cls.on
    else:
      return cls.off


class FanSpeed(Enum):
  low = 1
  medium = 2
  high = 3

  def __rshift__(self, target):
    # low -> medium => trigger x1
    # low -> high => trigger x2
    # medium -> low => trigger x2
    # medium -> high => trigger x1
    # high -> low => trigger x1
    # high -> medium => trigger x2

    if target.value < self.value:
      return target.value - self.value + 3
    else:
      return target.value - self.value

  @classmethod
  def from_value(cls, value):
    if value < 30:
      return cls.low
    if value < 60:
      return cls.medium
    if value <= 100:
      return cls.high


class IrRemote:
  def __init__(self, props=None):
    self.pins = self._setup_pins()

    self.state = AttrDict(
      power=ActiveState.off,
      swing=ActiveState.off,
      speed=FanSpeed.low)

    if props:
      self.state.power = ActiveState.from_value(props.active.value)
      self.state.swing = ActiveState.from_value(props.swing.value)
      self.state.speed = ActiveState.from_value(props.speed.value)

  def _setup_pins(self):
    pin_map = config.fan_remote.pin_map
    return AttrDict(
      vcc=gpio_pin(pin_map.VCC),
      pow=gpio_pin(pin_map.POW),
      osc=gpio_pin(pin_map.OSC),
      spd=gpio_pin(pin_map.SPD))

  def __exit__(self, *args, **kwargs):
    self.pins.vcc.off()
    sleep(0.1)
    for pid in ['pow', 'osc', 'spd']:
      self.pins[pid].on()
    sleep(0.2)

  def __enter__(self):
    for pid in ['pow', 'osc', 'spd']:
      self.pins[pid].on()
    sleep(0.1)
    self.pins.vcc.on()
    sleep(0.2)

  def trigger(self, pin):
    with self:
      pin.off()
      sleep(0.4)
      pin.on()

  def verify_trigger(self):
    # Detect if the device beeped, otherwise try again!
    pass

  def power(self, state):
    if self.state.power != state:
      self.trigger(self.pins.pow)
      self.state.power = state

  def swing(self, state):
    if self.state.power != ActiveState.on:
      return
    if self.state.swing != state:
      self.trigger(self.pins.osc)
      self.state.swing = state

  def speed(self, target):
    if self.state.power != ActiveState.on:
      return
    for i in range(self.state.speed >> target):
      self.trigger(self.pins.spd)
    self.state.speed = target

  def __del__(self):
    for pid, pin in self.pins.items():
      pin.close()


class TristarFan(AsyncAccessory):
  category = CATEGORY_FAN

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.set_info_service(
      firmware_revision='v1.0',
      manufacturer='noop.pw',
      model='pw.noop.hap.tristar_ir',
      serial_number='42-AC-TRISTARIR')

    fan = self.add_preload_service('Fanv2', chars=[
      'Active',
      'SwingMode',
      'RotationSpeed',
      'CurrentFanState',
      'RotationDirection',
    ])

    self.props = AttrDict(
      active=fan.configure_char('Active', setter_callback=self.toggle_power),
      swing=fan.configure_char('SwingMode', setter_callback=self.toggle_swing),
      speed=fan.configure_char('RotationSpeed', setter_callback=self.toggle_speed),
      fan_state=fan.configure_char('CurrentFanState'),
      fan_rotation_dir=fan.configure_char('RotationDirection', value=0))

    self.remote = IrRemote(self.props)

  def toggle_power(self, value):
    self.remote.power(ActiveState.from_value(value))

  def toggle_swing(self, value):
    self.remote.swing(ActiveState.from_value(value))

  def toggle_speed(self, value):
    self.remote.speed(FanSpeed.from_value(value))

  @AsyncAccessory.run_at_interval(5)
  async def run(self):
    self.props.fan_state.set_value(self.remote.state.active == ActiveState.on)
