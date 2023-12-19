import machine
import uasyncio

from buzzerclient import BuzzerServerClient, BuzzerHttpClient
from buzzergame import BuzzerGame, BuzzerHardwareWrapper
from clienthandler import ClientHandler
from config import Config
from configbasedbootstrap import ConfigBasedBootstrap
from configmanager import ConfigManager
from logger import Logger, Logging
from microwebserver import WebHelper
from nonconfigbootstrap import NonConfigBootstrap
from wifimanager import WiFiManager

html_stop_game = """<!DOCTYPE html>
<html>
<head>
    <title>Buzzer Game</title>
</head>
<body>
    <h2>Do you want stop the game</h2>
    <form action="/game_stop" method="post">   
        <input type="submit" value="Stop Training">
    </form>    
</body>
</html>
"""

html_buzzer = """<!DOCTYPE html>
<html>
<head>
    <title>Buzzer Game</title>
</head>
<body>
    <h2>Do you want play a game</h2>
    <form action="/game_start" method="post">   
        <input type="submit" value="Start Training">
    </form>    
</body>
</html>
"""

# HTML page served to the client
html_page = """<!DOCTYPE html>
<html>
<head>
    <title>WiFi Configuration</title>
</head>
<body>
    <h2>WiFi Configuration</h2>
    <form action="/save" method="post">
        <label for="name">Name of the buzzer:</label>
        <input type="text" id="name" name="name" value="buzzerserver" required><br>   
        <label for="is_server">Is Server:</label>
        <input type="checkbox" id="is_server" name="is_server"><br>
        <label for="servername">Name of the server:</label>
        <input type="text" id="servername" name="servername" value="buzzerserver" required><br>                    
        <label for="ssid">SSID:</label>
        <input type="text" id="ssid" name="ssid" value="ssid" required><br>
        <label for="password">Password:</label>
        <input type="password" id="password" value="password" name="password" required><br>
        <input type="submit" value="Save">
    </form>
</body>
</html>
"""


def show_game_page():
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += html_buzzer
    return response


def start_new_game(post_data):
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += html_stop_game

    game.start_game()

    return response


def stop_new_game(post_data):
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += "Go back to <a href='/'>overview</a>"

    game.stop_game()

    return response


def delete_config_page():
    game.switch_off_led()
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += "<html><body><h2>Removed Config File</h2></body></html>"

    configManager.remove_config()
    return response


def show_access_point_landing_page():
    return html_page


def handle_client_page(post_data):
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    client_name = post_data.split('&')[0].split('=')[1]
    button_pressed = post_data.split('&')[1].split('=')[1] == "yes"
    light_on = post_data.split('&')[2].split('=')[1] == "yes"
    response += clientHandler.handle_client(client_name, button_pressed, light_on)

    return response


def save_wifi_settings(post_data):
    game.switch_off_led()
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    response += "<html><body><h2>WiFi configuration saved. Pico will now try to connect to the new " \
                "WLAN. Please restart the pico</h2></body></html>"

    parsed_data = WebHelper.extract_post_data(post_data)

    name = parsed_data['name']
    is_server = "is_server" in parsed_data and parsed_data['is_server'] == 'on'
    servername = parsed_data['servername']
    ssid = parsed_data['ssid']
    password = parsed_data['password']

    configManager.write_config(
        Config(is_server=is_server, name=name, servername=servername, ssid=ssid, password=password))

    return response


logger = Logger(name="Buzzer", level=Logging.DEBUG)
annode = machine.Pin(13, machine.Pin.OUT, machine.Pin.PULL_DOWN)
r = machine.Pin(15, machine.Pin.OUT, machine.Pin.PULL_DOWN)
g = machine.Pin(14, machine.Pin.OUT, machine.Pin.PULL_DOWN)
b = machine.Pin(12, machine.Pin.OUT, machine.Pin.PULL_DOWN)
button = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)

clientHandler = ClientHandler(20)
hwWrapper = BuzzerHardwareWrapper(annode, r, g, b, button, True)
game = BuzzerGame(hwWrapper, clientHandler)
configManager = ConfigManager()
config = configManager.read_config()
configManager.remove_config()

if config is not None:
    if config.is_server:
        event_loop = uasyncio.get_event_loop()
        bootstrap = ConfigBasedBootstrap(config, 80, hwWrapper, configManager.remove_config)
        uasyncio.run(
            bootstrap.boot(show_game_page, delete_config_page, start_new_game, stop_new_game, handle_client_page))
        buzzerServerClient = BuzzerServerClient(hwWrapper, config, clientHandler)
        uasyncio.run(buzzerServerClient.start(10, 1))
        event_loop.run_forever()
    else:
        is_connected, ip_address = WiFiManager().connect_to_wifi(config.ssid, config.password, config.name)
        if is_connected:
            logger.info("Main", "Connected to wifi with ip address: {}".format(ip_address))
        else:
            logger.error("Main", "Not connected to wifi")
        event_loop = uasyncio.get_event_loop()
        buzzerServerClient = BuzzerHttpClient(5, 1, hwWrapper, config)
        uasyncio.run(buzzerServerClient.start())
        event_loop.run_forever()
else:
    event_loop = uasyncio.get_event_loop()
    bootstrap = NonConfigBootstrap("pico_buzzer", "1234567890", 80)
    server_task = bootstrap.boot(show_access_point_landing_page, save_wifi_settings)
    uasyncio.run(server_task)
    event_loop.run_forever()
