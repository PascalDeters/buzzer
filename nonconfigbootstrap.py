import machine

from config import Config
from logger import Logger
from microwebserver import MicroWebServer, WebHelper
from wifimanager import WiFiManager


class NonConfigBootstrap:
    def __init__(self, ssid, password, port, configManager, buzzerGame):
        self.ssid = ssid
        self.password = password
        self.port = port
        self.webserver = None
        self.logger = Logger()
        self.caller = "NonConfigBootstrap"
        self.configManager = configManager
        self.game = buzzerGame

    async def boot(self):
        ip_address = WiFiManager().start_access_point(self.ssid, self.password)

        self.webserver = MicroWebServer(ip_address, self.port)
        self.webserver.add_get_handler("/", self.__ap_configuration__)
        self.webserver.add_get_handler("/min.css", self.__show_css__)
        self.webserver.add_post_handler("/save", self.__save_and_close_server__)
        await self.webserver.start_server()

    def __ap_configuration__(self):
        response = WebHelper.get_content_type_html()
        response += WebHelper.get_web_content("ap_config_page.html")
        return response

    def __save_and_close_server__(self, post_data):
        response = self.__save_wifi_settings__(post_data)
        machine.reset()
        return response

    def __save_wifi_settings__(self, post_data):
        self.game.switch_off_led()
        response = WebHelper.get_content_type_html()
        response += WebHelper.get_web_content("ap_config_saved.html")

        parsed_data = WebHelper.extract_post_data(post_data)

        self.logger.debug(self.logger, "Parsed data: {}".format(parsed_data))

        name = parsed_data['name']
        is_server = "is_server" in parsed_data and parsed_data['is_server'] == 'on'
        servername = parsed_data['servername']
        ssid = parsed_data['ssid']
        password = parsed_data['password']

        self.configManager.write_config(
            Config(is_server=is_server, name=name, servername=servername, ssid=ssid, password=password))

        return response

    def __show_css__(self):
        response = WebHelper.get_content_type_css()
        response += WebHelper.get_web_content("pure.min.css")
        return response
