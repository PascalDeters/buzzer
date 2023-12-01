import utime


class Logging:
    DEBUG = 1
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITCAL = 50


class Logger:
    _instance = None

    def __new__(cls, name="MyLogger", level=Logging.DEBUG):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.level = level
            cls._instance.name = name
        return cls._instance

    def debug(self, caller, message):
        self.__message__(caller, message, Logging.DEBUG)

    def info(self, caller, message):
        self.__message__(caller, message, Logging.INFO)

    def warning(self, caller, message):
        self.__message__(caller, message, Logging.WARNING)

    def error(self, caller, message):
        self.__message__(caller, message, Logging.ERROR)

    def critical(self, caller, message):
        self.__message__(caller, message, Logging.CRITCAL)

    def __message__(self, caller: str, message: str, log_level):
        if log_level >= self._instance.level:
            full_caller = self.__ljust__("[{}.{}]".format(self.name, caller), 25)
            time = utime.time()
            print("[{}] {} [{}] {}".format(time, full_caller, self.__ljust__(self.__level_to_str(log_level), 7), message))

    def __ljust__(self, s, width, fillchar=' '):
        if len(s) >= width:
            return s
        else:
            return s + fillchar * (width - len(s))

    def __level_to_str(self, log_level):
        if log_level == Logging.INFO:
            return "INFO"
        if log_level == Logging.DEBUG:
            return "DEBUG"
        if log_level == Logging.WARNING:
            return "WARNING"
        if log_level == Logging.ERROR:
            return "ERROR"
        if log_level == Logging.CRITCAL:
            return "CRITCAL"
