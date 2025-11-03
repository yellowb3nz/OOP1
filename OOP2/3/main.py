import re
from datetime import datetime
from typing import Protocol, List


class Logger:
    def __init__(self, filters: List['LogFilterProtocol'], handlers: List['LogHandlerProtocol']):
        self.filters = filters
        self.handlers = handlers
    
    def log(self, text: str):
        for log_filter in self.filters:
            if not log_filter.match(text):
                return
        
        for handler in self.handlers:
            handler.handle(text)


class LogFilterProtocol(Protocol):
    def match(self, text: str) -> bool:
        return True


class SimpleLogFilter:
    def __init__(self, pattern: str):
        self.pattern = pattern
    
    def match(self, text: str) -> bool:
        return self.pattern in text


class ReLogFilter:
    def __init__(self, pattern: str):
        self.pattern = pattern
    
    def match(self, text: str) -> bool:
        return bool(re.match(self.pattern, text))


class LogHandlerProtocol(Protocol):
    def handle(self, log_text: str) -> None:
        pass


class FileHandler:
    def __init__(self, filename: str):
        self.filename = filename
    
    def handle(self, log_text: str) -> None:
        try:
            f = open(self.filename, 'a', encoding='utf-8')
            timestamp = datetime.today().isoformat(sep='|')
            log_entry = f'LOG at [{timestamp}] : {log_text}\n'
            f.write(log_entry)
            f.close()
        except:
            raise FileNotFoundError("файла с таким именем не существует!")


class ConsoleHandler:
    def handle(self, log_text: str) -> None:
        timestamp = datetime.today().isoformat(sep='|')
        print(f'LOG at [{timestamp}] : {log_text}')


class SocketHandler:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def handle(self, log_text: str) -> None:
        print("//СДЕЛАЕМ ВИД ЧТО ЭТОТ ЛОГ ПЕРЕДАЛСЯ КУДА-ТО ЧЕРЕЗ СОКЕТ")
        timestamp = datetime.today().isoformat(sep='|')
        print(f'SOCKET-LOG at [{timestamp}] : {log_text}')


class SysLogHandler:
    def handle(self, log_text: str) -> None:
        print("//СДЕЛАЕМ ВИД ЧТО ЭТОТ ЛОГ ЗАПИСАЛСЯ В СИСТЕМУ")
        timestamp = datetime.today().isoformat(sep='|')
        print(f'SYS-LOG at [{timestamp}] : {log_text}')

############################################################

if __name__ == '__main__':
    
    error_filter = SimpleLogFilter("ERROR")
    warn_filter = SimpleLogFilter("WARN")
    http_filter = ReLogFilter(r"HTTP/\d\.\d")

    file_handler = FileHandler("C:\\Users\\Danya\\Desktop\\OOP2\\3\\logs.log")
    console_handler = ConsoleHandler()
    socket_handler = SocketHandler("127.0.0.1", 8080)
    syslog_handler = SysLogHandler()

    error_logger = Logger(filters=[error_filter], handlers=[console_handler, file_handler, syslog_handler])
    warn_logger = Logger(filters=[warn_filter], handlers=[console_handler, file_handler])
    http_logger = Logger(filters=[http_filter], handlers=[socket_handler])

    error_logger.log("[ERROR]: any error1")
    error_logger.log("[ERROR]: any error2")
    error_logger.log("[WARN]: any warning1")
    error_logger.log("[WARN]: any warning2")
    error_logger.log("[WARN]: any warning3")
    warn_logger.log("[WARN]: any warning4")
    warn_logger.log("[WARN]: any warning5")
    http_logger.log("HTTP/1.1 404")
    http_logger.log("connection failed")
