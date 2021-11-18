"""Серверная часть"""
import select
import socket
import sys
import json
import argparse
import time
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, SENDER, MSG, MSG_TEXT
from common.utils import get_message, send_message, validate_ip, validate_port
import logging
import logs.confs.server_log_config
from decos import Log
log = logging.getLogger('app.server')


class Server:

    @Log()
    def process_client_message(self, message, message_list, client):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :param message_list:
        :param client:
        :return:
        '''

        # Если сообщение о присутствии
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            send_message(client, {RESPONSE: 200})
            return
        # Если обычное сообщение
        elif ACTION in message and message[ACTION] == MSG and \
                TIME in message and MSG_TEXT in message:
            message_list.append((message[ACCOUNT_NAME], message[MSG_TEXT]))
            return
        else:
            log.warning('Принято некорректное сообщение от клиента.')
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            })
            return

    @Log()
    def arg_parser(self):
        """Парсер аргументов коммандной строки"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        listen_address = namespace.a
        listen_port = namespace.p

        # валидация аргументов
        validate_port(listen_port)
        validate_ip(listen_address)

        return listen_address, listen_port

    @Log()
    def main(self):
        '''
        Загрузка параметров командной строки. Если нет параметров, то задаём значения по умоланию.
        Сначала обрабатываем порт:
        server.py -p 4242 -a 192.168.88.254
        :return:
        '''
        log.info('Попытка запуска сервера')
        listen_address, listen_port = self.arg_parser()

        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))
        transport.settimeout(0.2)

        # Cписок клиентов, очередь сообщений
        clients = []
        messages = []

        # Слушаем порт
        transport.listen(MAX_CONNECTIONS)
        log.info('Удачный запуск сервера')

        while True:
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []

            # Проверяем на наличие ждущих клиентов
            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            # Принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка - исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message),
                                                messages, client_with_message)
                    except:
                        log.info(f'Клиент {client_with_message.getpeername()} '
                                 f'отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            if messages and send_data_lst:
                message = {
                    ACTION: MSG,
                    SENDER: messages[0][0],
                    TIME: time.time(),
                    MSG_TEXT: messages[0][1]
                }
                del messages[0]
                for waiting_client in send_data_lst:
                    try:
                        send_message(waiting_client, message)
                    except:
                        log.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        clients.remove(waiting_client)


if __name__ == '__main__':
    new_server = Server()
    Server.main(new_server)
