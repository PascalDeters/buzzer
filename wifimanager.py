import network
import utime

from logger import Logger


class WiFiManager:
    def __init__(self):
        self.access_point = network.WLAN(network.AP_IF)
        self.wlan_client = network.WLAN(network.STA_IF)
        self.logger = Logger()
        self.caller = "WifiManager"

    def start_access_point(self, ssid, password, hostname: ""):
        self.logger.debug(self.caller, "Host and open WLAN. SSID: {}, with Password: {}".format(ssid, password))
        if hostname is not "":
            self.logger.debug(self.caller, "Setting hostname: {}".format(hostname))
            self.access_point.config(hostname=hostname)

        self.access_point.config(essid=ssid, password=password)
        # Enable access point mode
        self.access_point.active(True)

        ip_address = self.access_point.ifconfig()[0]
        self.logger.debug(self.caller, "Access Point started. SSID: {}, with Password: {}, and IP-Addr. {}".format(ssid, password, ip_address))

        return ip_address

    def connect_to_wifi(self, ssid, password, hostname: ""):
        self.logger.debug(self.caller, "Connecting to WLAN. SSID: {}, with Password: {}".format(ssid, password))
        if hostname is not "":
            self.logger.debug(self.caller, "Setting hostname: {}".format(hostname))
            self.wlan_client.config(hostname=hostname)

        # Enable station mode
        self.wlan_client.active(True)
        self.wlan_client.connect(ssid, password)

        # Wait for the connection to be established
        timeout = 20  # seconds
        start_time = utime.time()
        while not self.wlan_client.isconnected():
            if utime.time() - start_time > timeout:
                self.logger.error(self.caller, "Failed to connect to WiFi within the timeout period.")
                return False, None
            utime.sleep(1)

        return self.wlan_client.isconnected(), self.wlan_client.ifconfig()[0]
