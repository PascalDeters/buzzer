from logger import Logger
from microwebserver import MicroWebServer, WebHelper
from wifimanager import WiFiManager

class ConfigBasedBootstrap:
    def __init__(self, port, hwWrapper, clientHandler, buzzerGame, confiManager):
        self.port = port
        self.hwWrapper = hwWrapper
        self.logger = Logger()
        self.caller = "ConfigBasedBootstrap"
        self.clientHandler = clientHandler
        self.game = buzzerGame
        self.configManager = confiManager
        self.config = self.configManager.read_config()

    async def boot(self):
        #is_connected, ip_address = WiFiManager().connect_to_wifi(self.config.ssid, self.config.password, self.config.name)
        ip_address = WiFiManager().start_access_point(self.config.ssid, self.config.password, self.config.name)

        if ip_address:
            self.logger.info(self.caller, "Connected to wifi with ip address: {}".format(ip_address))
            webserver = MicroWebServer(ip_address, 80)

            webserver.add_get_handler("/", self.__show_overview__)
            webserver.add_get_handler("/min.css", self.__show_css__)
            webserver.add_get_handler("/delete_config", self.__delete_config__)
            webserver.add_post_handler("/client", self.__handle_client__)
            webserver.add_post_handler("/game_start", self.__game_start__)
            webserver.add_post_handler("/game_stop", self.__game_stop__)

            return await webserver.start_server()
        else:
            self.logger.error(self.caller, "Not connected to wifi")

    def __delete_config__(self):
        self.game.switch_off_led()
        response = WebHelper.get_content_type_html()
        response += WebHelper.get_web_content("delete_config.html")

        self.configManager.remove_config()
        return response

    def __show_overview__(self):
        response = WebHelper.get_content_type_html()
        response += WebHelper.get_web_content("game_start.html")
        return response

    def __game_start__(self, post_data):
        response = WebHelper.get_content_type_html()
        response += WebHelper.get_web_content("game_stop.html")

        self.game.start_game()
        return response

    def __game_stop__(self, post_data):
        response = WebHelper.get_content_type_html()
        response += WebHelper.get_web_content("game_stopped.html")
        self.game.stop_game()
        return response

    def __handle_client__(self, post_data):
        response = WebHelper.get_content_type_html()
        client_name = post_data.split('&')[0].split('=')[1]
        button_pressed = post_data.split('&')[1].split('=')[1] == "yes"
        light_on = post_data.split('&')[2].split('=')[1] == "yes"
        response += self.clientHandler.handle_client(client_name, button_pressed, light_on)
        return response

    def __show_css__(self):
        response = WebHelper.get_content_type_css()
        response += WebHelper.get_web_content("pure.min.css")
        return response
