import _thread
import asyncio
import sys

import uasyncio
import utime as utime
import urequests as requests

from logger import Logger


class BuzzerHttpClient:
    def __init__(self, delay_to_start, interval, hwWrapper, config):
        self.delay_to_start = delay_to_start
        self.hwWrapper = hwWrapper
        self.interval = interval
        self.config = config
        self.command = ""
        self.button_pressed = False
        self.logger = Logger()
        self.caller = "BuzzerHttpClient"

    async def start(self):
        self.logger.debug(self.caller, "Start")
        _thread.start_new_thread(self.__check_button__, ())
        await asyncio.sleep(self.delay_to_start)
        return await uasyncio.create_task(self.__loop__())

    def __check_button__(self):
        while True:
            if self.hwWrapper.button.value() == 0:
                if self.command == "light_on":
                    self.button_pressed = True
                    self.hwWrapper.off()
                    self.logger.info(self.caller, "The right button was pressed")
                utime.sleep(0.10)

    async def __loop__(self):
        while True:
            if self.button_pressed:
                button_state = "yes"
            else:
                button_state = "no"
            url_encoded_data = "client_name={}&button_pressed={}&light_on={}".format(self.config.name, button_state, "no")
            self.logger.debug(self.caller, "Try to reach server [{}] with data [{}]".format(self.config.servername, url_encoded_data))
            response = None
            try:
                response = requests.post("http://{}/client".format(self.config.servername), data=url_encoded_data)
                self.logger.debug(self.caller, "Server response: {}".format(response.text))

                self.command = response.text

                if self.button_pressed:
                    self.button_pressed = False
                if self.command == "light_on":
                    self.hwWrapper.on()
                else:
                    self.hwWrapper.off()
            except Exception as e:
                self.logger.error(self.caller, "Exception: {}".format(e))
                sys.print_exception(e)
            finally:
                if response is not None:
                    response.close()

            await asyncio.sleep(self.interval)


class BuzzerServerClient:

    def __init__(self, hwWrapper, config, clientHandler):
        self.config = config
        self.hwWrapper = hwWrapper
        self.light_on = False
        self.button_pressed = False
        self.clientHandler = clientHandler
        self.logger = Logger()
        self.caller = "BuzzerServerClient"

    async def start(self, delay_to_start=10, interval=1):
        self.logger.debug(self.caller, "Start")
        _thread.start_new_thread(self.__check_button__, ())
        await asyncio.sleep(delay_to_start)
        return await uasyncio.create_task(self.__loop__(interval))

    def __check_button__(self):
        while True:
            if self.hwWrapper.button.value() == 0:
                if self.clientHandler.any_client_with_a_command() and self.config.name in self.clientHandler.clients:
                    clientConfig = self.clientHandler.clients[self.config.name]
                    if clientConfig.command == "light_on":
                        self.button_pressed = True
                        self.hwWrapper.off()
                        self.logger.info(self.caller, "The right button was pressed")
                utime.sleep(0.10)

    async def __loop__(self, interval):
        while True:
            command = self.clientHandler.handle_client(self.config.name, self.button_pressed, self.light_on)
            if self.button_pressed:
                self.button_pressed = False
            if command == "light_on":
                self.hwWrapper.on()
            else:
                self.hwWrapper.off()

            await asyncio.sleep(interval)
