"""Общие утилиты"""

import sys
import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING


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


def validate_ip(ip_address):
    '''
    Утилита для валидации полученного ip-адреса.
    Принимает строку.
    :param ip_address:
    :return :
    '''
    try:
        octets = ip_address.split('.')
        if len(octets) != 4:
            raise ValueError
        for octet in octets:
            if not octet.isdigit():
                raise ValueError
            i = int(octet)
            if i < 0 or i > 255:
                raise ValueError
    except ValueError:
        print('Неверный формат IP-адреса.')
        sys.exit(1)


def validate_port(port):
    '''
    Утилита для валидации полученного порта.
    Принимает строку.
    :param port:
    :return :
    '''
    try:
        if not 1024 <= int(port) <= 65535:
            raise ValueError
    except ValueError:
        print('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
