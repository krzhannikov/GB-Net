"""Общие утилиты"""

import sys
import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
import logging
import logs.confs.client_log_config
import logs.confs.server_log_config
log_client = logging.getLogger('app.client')
log_server = logging.getLogger('app.server')


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


def validate_ip(ip_address, checker='client'):
    '''
    Утилита для валидации полученного ip-адреса.
    Принимает строку.
    :param ip_address:
    :param checker:
    '''
    try:
        octets = ip_address.split('.')
        if len(octets) != 4:
            if checker == 'server':
                log_server.critical('IP-адрес должен состоять из четырёх октетов. Остановка сервера.')
            else:
                log_client.critical('IP-адрес должен состоять из четырёх октетов. Остановка клиента.')
            raise ValueError
        for octet in octets:
            if not octet.isdigit():
                if checker == 'server':
                    log_server.critical('Каждый октет должен состоять из цифр. Остановка сервера.')
                else:
                    log_client.critical('Каждый октет должен состоять из цифр. Остановка клиента.')
                raise ValueError
            i = int(octet)
            if i < 0 or i > 255:
                if checker == 'server':
                    log_server.critical('Каждый октет должен быть в диапазоне от 0 до 255. Остановка сервера.')
                else:
                    log_client.critical('Каждый октет должен быть в диапазоне от 0 до 255. Остановка клиента.')
                raise ValueError
    except ValueError:
        if checker == 'server':
            log_server.critical('Неверный формат IP-адреса. Остановка сервера.')
        else:
            log_client.critical('Неверный формат IP-адреса. Остановка клиента.')
        # sys.exit(1)
        raise  # вызываем исключение повторно для прохождения тестов в test_utils.py


def validate_port(port, checker='client'):
    '''
    Утилита для валидации полученного порта.
    Принимает строку.
    :param port:
    :param checker:
    '''
    try:
        if not 1024 <= int(port) <= 65535:
            if checker == 'server':
                log_server.critical('Порт должен быть в диапазоне от 1024 до 65535. Остановка сервера.')
            else:
                log_client.critical('Порт должен быть в диапазоне от 1024 до 65535. Остановка клиента.')
            raise ValueError
    except ValueError:
        if checker == 'server':
            log_server.critical('В качастве порта может быть указано только число '
                                'в диапазоне от 1024 до 65535. Остановка сервера.')
        else:
            log_client.critical('В качастве порта может быть указано только число '
                                'в диапазоне от 1024 до 65535. Остановка клиента.')
        # sys.exit(1)
        raise  # вызываем исключение повторно для прохождения тестов в test_utils.py
