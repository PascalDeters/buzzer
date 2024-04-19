import time

from logger import Logger


class BuzzerHardwareWrapper:
    def __init__(self, annode, r, g, b, button, is_rgb_led):
        self.annode = annode
        self.r = r
        self.g = g
        self.b = b
        self.button = button
        self.is_rgb_led = is_rgb_led
        self.annode.off()

    def off(self):
        if self.is_rgb_led:
            self.annode.off()
            self.r.off()
            self.b.off()
            self.g.off()
        else:
            self.r.off()

    def on(self):
        if self.is_rgb_led:
            self.annode.off()
            self.r.off()
            self.b.on()
            self.g.on()
        else:
            self.r.on()

    def blink_r_g_b(self):
        if self.is_rgb_led:
            self.annode.off()
            self.r.on()
            time.sleep(0.25)
            self.r.off()
            self.b.on()
            time.sleep(0.25)
            self.b.off()
            self.g.on()
            time.sleep(0.25)
            self.g.off()
        else:
            self.r.on()

    def blink_green(self):
        if self.is_rgb_led:
            self.annode.off()
            self.g.on()
            time.sleep(1)
            self.g.off()

            self.g.on()
            time.sleep(1)
            self.g.off()

            self.g.on()
            time.sleep(1)
            self.g.off()
        else:
            self.g.on()

    def blink_red(self):
        if self.is_rgb_led:
            self.annode.off()
            self.r.on()
            time.sleep(1)
            self.r.off()

            self.r.on()
            time.sleep(1)
            self.r.off()

            self.r.on()
            time.sleep(1)
            self.r.off()
        else:
            self.r.on()

class BuzzerGame:

    def __init__(self, hwWrapper, clientHandler):
        self.logger = Logger()
        self.caller = "BuzzerGame"
        self.hwWrapper = hwWrapper
        self.is_game_active = True
        self.clientHandler = clientHandler
        self.clientHandler.client_timeout_handler = self.__handle_client_timeout__
        self.clientHandler.client_said_hello_handler = self.__handle_client_hello__

    def switch_on_led(self):
        self.hwWrapper.on()
        self.logger.debug(self.caller, "LED switched on")

    def switch_off_led(self):
        self.hwWrapper.off()
        self.logger.debug(self.caller, "LED switched off")

    def stop_game(self):
        self.switch_off_led()
        self.is_game_active = False
        self.switch_off_led()
        self.clientHandler.clear_all_commands()

    def start_game(self):
        self.is_game_active = True
        self.__start_light_for_random_client__()

    def __handle_client_hello__(self, client_name):
        client = self.clientHandler.clients[client_name]
        self.logger.debug(self.caller, "received a command [{}] from client [{}]".format(client.command, client.name))

        if client.command == "light_on" and client.button_pressed is True:
            self.logger.info(self.caller, "Someone hit the right buzzer [{}] :). Going to active another one".format(client.name))
            client.reset()

        self.__handle_filled_command_queue()

    def __handle_client_timeout__(self, client_name):
        self.logger.warning(self.caller, "Client [{}] has reached a timeout".format(client_name))
        self.__handle_filled_command_queue()

    def __handle_filled_command_queue(self):
        if self.is_game_active and self.clientHandler.any_client_with_a_command() is False:
            self.logger.debug(self.caller, "There are no clients left with a command ... ")
            self.__start_light_for_random_client__()

    def __start_light_for_random_client__(self):
        if self.clientHandler.any_clients():
            client = self.clientHandler.get_random_client()
            self.clientHandler.add_command(client.name, "light_on")
            self.logger.info(self.caller, "Start a new game and Client [{}] should switch on the light".format(client.name))
        else:
            self.logger.info(self.caller, "Couldnt start game because no clients have registered so far...")

    def __start_game_in_thread__(self):
        self.switch_on_led()
        return ""
