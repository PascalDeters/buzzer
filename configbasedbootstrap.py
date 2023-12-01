from logger import Logger
from microwebserver import MicroWebServer
from wifimanager import WiFiManager

class ConfigBasedBootstrap:
    def __init__(self, config, port, hwWrapper, remove_config_handler):
        self.config = config
        self.port = port
        self.hwWrapper = hwWrapper
        self.remove_config_handler = remove_config_handler
        self.logger = Logger()
        self.caller = "ConfigBasedBootstrap"

    async def boot(self, show_game_page, delete_config_page, start_new_game_page, stop_new_game_page, handle_client_page):
        is_connected, ip_address = WiFiManager().connect_to_wifi(self.config.ssid, self.config.password,
                                                                 self.config.name)

        if is_connected:
            self.logger.info(self.caller, "Connected to wifi with ip address: {}".format(ip_address))
            webserver = MicroWebServer(self.config.name, 80)

            webserver.add_get_handler("/", show_game_page)
            webserver.add_get_handler("/reset", delete_config_page)
            webserver.add_post_handler("/client", handle_client_page)
            webserver.add_post_handler("/game_start", start_new_game_page)
            webserver.add_post_handler("/game_stop", stop_new_game_page)

            return await webserver.start_server()
        else:
            self.logger.error(self.caller, "Not connected to wifi")

