"""Клиентская часть"""

import sys
import json
import socket
import time
import argparse
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, SENDER, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MSG, MSG_TEXT
from common.utils import get_message, send_message, validate_ip, validate_port
import logging
import logs.confs.client_log_config
from decos import Log
log = logging.getLogger('app.client')


class Client:

    @Log()
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

    @Log()
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

    @Log()
    def message_from_server(self, message):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        if ACTION in message and message[ACTION] == MSG and \
                SENDER in message and MSG_TEXT in message:
            print(f'Получено сообщение от пользователя '
                  f'{message[SENDER]}:{message[MSG_TEXT]}')
            log.info(f'Получено сообщение от пользователя '
                        f'{message[SENDER]}:{message[MSG_TEXT]}')
        else:
            log.error(f'Получено некорректное сообщение с сервера: {message}')

    @Log()
    def create_message(self, sock, account_name='Guest'):
        """Функция запрашивает текст сообщения и возвращает его.
        Также завершает работу при вводе подобной команды
        """
        message = input('Введите сообщение для отправки или \'quit\' для завершения работы: ')
        if message == 'quit':
            sock.close()
            log.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            ACTION: MSG,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MSG_TEXT: message
        }
        log.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

    @Log()
    def arg_parser(self):
        """Парсер аргументов коммандной строки"""
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-m', '--mode', default='listen', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = namespace.port
        client_mode = namespace.mode

        # валидация аргументов
        # client.py 192.168.88.254 4242 -m listen
        validate_port(server_port)
        validate_ip(server_address)
        if client_mode not in ('listen', 'send'):
            log.critical(f'Указан недопустимый режим работы {client_mode}, '
                         f'допустимые режимы: listen , send')
            sys.exit(1)

        return server_address, server_port, client_mode

    @Log()
    def main(self):
        """Загружаем параметы коммандной строки"""
        server_address, server_port, client_mode = self.arg_parser()

        log.info(
            f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
            f'порт: {server_port}, режим работы: {client_mode}')

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
        else:
            # Если соединение с сервером установлено, начинаем обмен сообщениями
            while True:
                # Режим работы - отправка сообщений
                if client_mode == 'send':
                    try:
                        send_message(transport, self.create_message(transport))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        log.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)

                # Режим работы - приём сообщений:
                if client_mode == 'listen':
                    try:
                        self.message_from_server(get_message(transport))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        log.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)


if __name__ == '__main__':
    new_client = Client()
    Client.main(new_client)
