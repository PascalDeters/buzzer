import random

import utime

from logger import Logger


class Client:
    def __init__(self, name, button_state, light_state):
        self.name = name
        self.ttl = utime.time()
        self.command = ""
        self.button_pressed = button_state
        self.light_on = light_state

    def reset(self):
        self.command = ""
        self.button_pressed = False
        self.light_on = False

class ClientHandler:

    def __init__(self, timeout):
        self.clients = {}
        self.timeout = timeout
        self.client_said_hello_handler = None
        self.client_timeout_handler = None
        self.logger = Logger()
        self.caller = "ClientHandler"

    def handle_client(self, client_name, button_state, light_state):
        self.logger.debug(self.caller, "Handle client {} with button state {} and light state {}".format(client_name, button_state, light_state))

        self.__remove_clients_that_reached_timeout()

        if client_name not in self.clients:
            self.logger.debug(self.caller, "New client {} with button state {} and light state {}".format(client_name, button_state, light_state))
            self.clients[client_name] = Client(client_name, button_state, light_state)

        self.__client_said_hello__(client_name, button_state, light_state)
        return self.clients[client_name].command

    def any_client_with_a_command(self):
        for key in self.clients:
            if self.clients[key].command is not "":
                return True

        return False

    def clear_all_commands(self):
        self.logger.debug(self.caller, "going to clear all command")

        for key in self.clients:
            self.clients[key].command = ""
            self.clients[key].button_pressed = False
            self.clients[key].light_on = False

    def get_random_client(self):
        if self.any_clients() == 0:
            return None

        total_clients = len(self.clients)
        random_index = random.randint(0, total_clients - 1)
        return list(self.clients.values())[random_index]

    def any_clients(self):
        return len(self.clients) > 0

    def add_command(self, client_name, command):
        self.logger.debug(self.caller, "Add command {} to client {}".format(command, client_name))

        if client_name in self.clients:
            self.clients[client_name].command = command

    def remove_command(self, client_name):
        self.logger.debug(self.caller, "Remove command from client {}".format(client_name))

        if client_name in self.clients:
            self.clients[client_name].command = ""

    def __client_said_hello__(self, client_name, button_state, light_state):
        client = self.clients[client_name]
        client.ttl = utime.time()
        client.button_pressed = button_state
        client.light_on = light_state

        if self.client_said_hello_handler is not None:
            self.client_said_hello_handler(client_name)

    def __remove_clients_that_reached_timeout(self):
        for key in self.clients:
            if self.__is_client_dead__(key):
                del self.clients[key]
                self.client_timeout_handler(key)

    def __is_client_dead__(self, client_name):
        client = self.clients[client_name]
        is_dead = (utime.time() - client.ttl) > self.timeout

        if is_dead:
            self.logger.warning(self.caller, "Client {} is dead: {} ".format(client_name, is_dead))
        return is_dead
