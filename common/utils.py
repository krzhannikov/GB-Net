"""Общие утилиты"""

import sys
import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
import logging
import logs.confs.client_log_config
import logs.confs.server_log_config
from decos import Log

# Метод определения модуля, источника запуска.
# Метод find() возвращает индекс первого вхождения искомой подстроки,
# если оно найдено в данной строке. Если не найдено - возвращает -1.
# os.path.split(sys.argv[0])[1]
if sys.argv[0].find('client') == -1:
    # если не найден модуль client, то логируем сервер
    log = logging.getLogger('app.server')
else:
    log = logging.getLogger('app.client')


@Log()
def get_message(client):
    '''
    Утилита для приёма и декодирования сообщения.
    Принимает байты, отдаёт словарь. Если пришло что-то другое - выдаёт ошибку.
    :param client:
    :return:
    '''

    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@Log()
def send_message(sock, message):
    '''
    Утилита для кодирования и отправки сообщения.
    Принимает словарь, отправляет байты
    :param sock:
    :param message:
    :return:
    '''

    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)


@Log()
def validate_ip(ip_address):
    '''
    Утилита для валидации полученного ip-адреса.
    Принимает строку.
    :param ip_address:
    '''
    try:
        if ip_address == '':
            return
        octets = ip_address.split('.')
        if len(octets) != 4:
            log.critical('IP-адрес должен состоять из четырёх октетов. Остановка.')
            raise ValueError
        for octet in octets:
            if not octet.isdigit():
                log.critical('Каждый октет должен состоять из цифр. Остановка.')
                raise ValueError
            i = int(octet)
            if i < 0 or i > 255:
                log.critical('Каждый октет должен быть в диапазоне от 0 до 255. Остановка.')
                raise ValueError
    except ValueError:
        log.critical('Неверный формат IP-адреса. Остановка.')
        # sys.exit(1)
        raise  # вызываем исключение повторно для прохождения тестов в test_utils.py


@Log()
def validate_port(port):
    '''
    Утилита для валидации полученного порта.
    Принимает строку.
    :param port:
    '''
    try:
        if not 1024 <= int(port) <= 65535:
            log.critical('Порт должен быть в диапазоне от 1024 до 65535. Остановка.')
            raise ValueError
    except ValueError:
        log.critical('В качастве порта может быть указано только число '
                     'в диапазоне от 1024 до 65535. Остановка.')
        # sys.exit(1)
        raise  # вызываем исключение повторно для прохождения тестов в test_utils.py
