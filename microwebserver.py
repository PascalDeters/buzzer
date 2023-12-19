import sys

import uasyncio

from logger import Logger


class MicroWebServer:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.get_handlers = {}
        self.post_handlers = {}
        self.logger = Logger()
        self.caller = "MicroWebServer"

    async def get_headers(self, reader, max_headers=100, max_line_length=4096):
        headers = {}
        num_headers = 0

        while True:
            if num_headers >= max_headers:
                self.logger.error(self.caller, "Maximum number of headers reached")
                raise ValueError("Maximum number of headers reached")

            line = await reader.readline()

            if len(line) > max_line_length:
                self.logger.error(self.caller, "Header line too long")
                raise ValueError("Header line too long")

            if line == b'\r\n':
                break

            try:
                key, value = line.decode().strip().split(':', 1)
            except ValueError:
                self.logger.error(self.caller, "Ignoring invalid header, not containing colon: {}".format(line))
                continue

            headers[key.strip()] = value.strip()
            num_headers += 1

        return headers

    async def start_server(self):
        # setup server
        task = await uasyncio.create_task(uasyncio.start_server(self.serve_client, self.address, self.port))
        self.logger.info(self.caller, "Server listening on {}:{}".format(self.address, self.port))
        return task

    async def serve_client(self, reader, writer):
        try:
            self.logger.debug(self.caller, "Receive request from client")
            # Read the request line
            request_line = await reader.readline()
            method, path, version = request_line.decode().strip().split()
            headers = await self.get_headers(reader)

            if method == 'GET' and path in self.get_handlers:
                self.logger.debug(self.caller, "Receive a http GET request")
                writer.write(self.get_handlers[path]())
                await writer.drain()
            elif method == 'POST' and path in self.post_handlers:
                self.logger.debug(self.caller, "Receive a http POST request")
                content_length = int(headers.get('Content-Length', 0))
                post_data = await reader.readexactly(content_length)
                writer.write(self.post_handlers[path](post_data.decode('utf-8')))
                await writer.drain()
            else:
                self.logger.debug(self.caller, "Client requests a unknown path")
                writer.write("HTTP/1.0 404 Not Found\r\n\r\nNot Found")
                await writer.drain()
        except Exception as e:
            self.logger.error(self.caller, "Exception occurred: {}".format(e))
            sys.print_exception(e)
            writer.write("HTTP/1.0 500 Error\r\n\r\n")
            await writer.drain()

        await writer.wait_closed()
        self.logger.debug(self.caller, "Client requests handled")

    def add_get_handler(self, path, handler):
        self.get_handlers[path] = handler

    def add_post_handler(self, path, handler):
        self.post_handlers[path] = handler
