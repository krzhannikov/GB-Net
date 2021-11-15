"""Клиентская часть"""

import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message, validate_ip, validate_port
import logging
import logs.confs.client_log_config
log = logging.getLogger('app.client')


class Client:

    def create_presence(self, account_name='Guest'):
        '''
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        '''
        # {'action': 'presence', 'time': 1573756748.825346, 'user': {'account_name': 'Guest'}}
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        return out

    def process_ans(self, message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            log.warning('Был отправлен некорректный запрос.')
            return f'400 : {message[ERROR]}'
        raise ValueError

    def main(self):
        '''Загружаем параметры командной строки'''
        # client.py 192.168.88.254 4242
        try:
            server_address = sys.argv[1]
            server_port = int(sys.argv[2])
            validate_port(server_port)
            validate_ip(server_address)
        except IndexError:
            log.warning('Были введены некорректные порт/адрес. Подключаемся с параметрами по умолчанию')
            server_address = DEFAULT_IP_ADDRESS
            server_port = DEFAULT_PORT

        # Инициализация сокета и обмен

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = self.create_presence()
        send_message(transport, message_to_server)
        try:
            answer = self.process_ans(get_message(transport))
            log.debug(f'Ответ сервера - {answer}')
        except (ValueError, json.JSONDecodeError):
            log.warning('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    new_client = Client()
    Client.main(new_client)
