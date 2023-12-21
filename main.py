import machine
import uasyncio

from buzzerclient import BuzzerServerClient, BuzzerHttpClient
from buzzergame import BuzzerGame, BuzzerHardwareWrapper
from clienthandler import ClientHandler
from configbasedbootstrap import ConfigBasedBootstrap
from configmanager import ConfigManager
from logger import Logger, Logging
from nonconfigbootstrap import NonConfigBootstrap
from wifimanager import WiFiManager

# Constants
BUZZER_CLIENT_TIMEOUT = 20
WEBSERVER_PORT = 80
PICO_AP_SSID = "pico_buzzer"
PICO_AP_PASSWORD = "1234567890"
BUZZER_CLIENT_DELAY_TO_START_IN_SEC = 5
BUZZER_CLIENT_INTERVAL_IN_SEC = 1

# Hardware
rgb_led_anode = machine.Pin(13, machine.Pin.OUT, machine.Pin.PULL_DOWN)
red_led = machine.Pin(15, machine.Pin.OUT, machine.Pin.PULL_DOWN)
green_led = machine.Pin(14, machine.Pin.OUT, machine.Pin.PULL_DOWN)
blue_led = machine.Pin(12, machine.Pin.OUT, machine.Pin.PULL_DOWN)
button = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)

# Objects
logger = Logger(name="Buzzer", level=Logging.DEBUG)
clientHandler = ClientHandler(BUZZER_CLIENT_TIMEOUT)
hwWrapper = BuzzerHardwareWrapper(rgb_led_anode, red_led, green_led, blue_led, button, True)
game = BuzzerGame(hwWrapper, clientHandler)
configManager = ConfigManager()
config = configManager.read_config()
#configManager.remove_config()

# Main
if config is not None:
    if config.is_server:
        event_loop = uasyncio.get_event_loop()
        bootstrap = ConfigBasedBootstrap(WEBSERVER_PORT, hwWrapper, clientHandler, game, configManager)
        uasyncio.run(bootstrap.boot())
        buzzerServerClient = BuzzerServerClient(hwWrapper, config, clientHandler)
        uasyncio.run(buzzerServerClient.start(BUZZER_CLIENT_DELAY_TO_START_IN_SEC, BUZZER_CLIENT_INTERVAL_IN_SEC))
        event_loop.run_forever()
    else:
        is_connected, ip_address = WiFiManager().connect_to_wifi(config.ssid, config.password, config.name)
        if is_connected:
            logger.info("Main", "Connected to wifi with ip address: {}".format(ip_address))
        else:
            logger.error("Main", "Not connected to wifi")
        event_loop = uasyncio.get_event_loop()
        buzzerServerClient = BuzzerHttpClient(BUZZER_CLIENT_DELAY_TO_START_IN_SEC, BUZZER_CLIENT_INTERVAL_IN_SEC,
                                              hwWrapper, config)
        uasyncio.run(buzzerServerClient.start())
        event_loop.run_forever()
else:
    event_loop = uasyncio.get_event_loop()
    bootstrap = NonConfigBootstrap(PICO_AP_SSID, PICO_AP_PASSWORD, WEBSERVER_PORT, configManager, game)
    server_task = bootstrap.boot()
    uasyncio.run(server_task)
    event_loop.run_forever()
