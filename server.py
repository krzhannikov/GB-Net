"""Серверная часть"""

import socket
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message, validate_ip, validate_port
import logging
import logs.confs.server_log_config
from decos import Log
log = logging.getLogger('app.server')


class Server:

    @Log()
    def process_client_message(self, message):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        log.warning('Принято некорректное сообщение от клиента.')
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    @Log()
    def main(self):
        '''
        Загрузка параметров командной строки. Если нет параметров, то задаём значения по умоланию.
        Сначала обрабатываем порт:
        server.py -p 4242 -a 192.168.88.254
        :return:
        '''
        log.info('Попытка запуска сервера')

        try:
            if '-p' in sys.argv:
                listen_port = int(sys.argv[sys.argv.index('-p') + 1])
                validate_port(listen_port)
            else:
                listen_port = DEFAULT_PORT
        except IndexError:
            log.critical('После параметра -\'p\' необходимо указать номер порта. Сервер не запущен')
            sys.exit(1)

        # Затем загружаем какой адрес слушать

        try:
            if '-a' in sys.argv:
                listen_address = sys.argv[sys.argv.index('-a') + 1]
                validate_ip(listen_address)
            else:
                listen_address = ''  # слушаем на всех интерфейсах
        except IndexError:
            log.critical(
                'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер. Сервер не запущен')
            sys.exit(1)

        # Готовим сокет

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))

        # Слушаем порт

        transport.listen(MAX_CONNECTIONS)
        log.info('Удачный запуск сервера')

        while True:
            client, client_address = transport.accept()
            try:
                message_from_client = get_message(client)
                log.debug(f'Сообщение от клиента - {message_from_client}')
                # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
                response = self.process_client_message(message_from_client)
                send_message(client, response)
                client.close()
            except (ValueError, json.JSONDecodeError):
                log.warning('Принято некорректное сообщение от клиента.')
                client.close()


if __name__ == '__main__':
    new_server = Server()
    Server.main(new_server)
