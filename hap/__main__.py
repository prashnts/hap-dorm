import signal

from pyhap.accessory_driver import AccessoryDriver

from .bridge import bridge
from . import config

driver = AccessoryDriver(bridge, port=51826, persist_file=config.persist_file)

signal.signal(signal.SIGINT, driver.signal_handler)
signal.signal(signal.SIGTERM, driver.signal_handler)

if __name__ == '__main__':
  driver.start()
