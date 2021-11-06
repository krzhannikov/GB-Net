"""Общие константы"""

# Порт сервера по умолчанию
DEFAULT_PORT = 4242
# IP-адрес сервера по умолчанию
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальный размер сообщения (в байтах)
MAX_PACKAGE_LENGTH = 1024
# Кодировка
ENCODING = 'utf-8'

# Основные ключи протокола JIM:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# Другие ключи протокола:
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
AUTH = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'
