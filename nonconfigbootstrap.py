import machine

import uasyncio

from logger import Logger
from microwebserver import MicroWebServer
from wifimanager import WiFiManager


class NonConfigBootstrap:
    def __init__(self, ssid, password, port):
        self.ssid = ssid
        self.password = password
        self.port = port
        self.webserver = None
        self.saveHandler = None
        self.logger = Logger()
        self.caller = "NonConfigBootstrap"

    async def boot(self, landing_page, save_page, handle_css_file):
        ip_address = WiFiManager().start_access_point(self.ssid, self.password)
        self.saveHandler = save_page

        self.webserver = MicroWebServer(ip_address, self.port)
        self.webserver.add_get_handler("/", landing_page)
        self.webserver.add_get_handler("/min.css", handle_css_file)
        self.webserver.add_post_handler("/save", self.__save_and_close_server)
        await self.webserver.start_server()

    def __save_and_close_server(self, post_data):
        response = self.saveHandler(post_data)
        machine.reset()
        return response
