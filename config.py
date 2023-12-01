class Config:
    def __init__(self, is_server=False, name="", servername="", ssid="", password=""):
        self.is_server = is_server
        self.name = name
        self.servername = servername
        self.ssid = ssid
        self.password = password

    def to_dict(self):
        return {
            "is_server": self.is_server,
            "name": self.name,
            "ssid": self.ssid,
            "password": self.password,
            "servername": self.servername
        }

    def from_dict(self, data):
        self.is_server = data.get("is_server", False)
        self.name = data.get("name", "")
        self.ssid = data.get("ssid", "")
        self.password = data.get("password", "")
        self.servername = data.get("servername", "")