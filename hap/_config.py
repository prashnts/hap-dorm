from huey import RedisHuey
from walrus import Walrus
from addict import Dict as AttrDict

config = AttrDict()

config.meta.manufacturer = 'noop.pw'
config.meta.model = 'pw.noop.hap.{s}'

config.persist_file = './.hap-dorm/accessory.state'

config.fan_remote.pin_map = AttrDict(
  VCC=22,    # 3 in wiringpi
  SPD=23,    # 4 in wiringpi
  OSC=24,    # 5 in wiringpi
  POW=25,    # 6 in wiringpi
)

# Task Queue
huey = RedisHuey(result_store=False)

# Redis backend
walrus = Walrus()
