"""Серверная часть"""
import select
import socket
import sys
import json
import argparse
import time
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, SENDER, MSG, MSG_TEXT, DESTINATION, EXIT
from common.utils import get_message, send_message, validate_ip, validate_port
import logging
import logs.confs.server_log_config
from decos import Log
log = logging.getLogger('app.server')


class Server:

    @Log()
    def process_client_message(self, message, message_list, client, clients, names):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :param message_list:
        :param client:
        :param clients:
        :param names:
        :return:
        '''

        # Если сообщение о присутствии
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, {RESPONSE: 200})
            else:
                response = dict()
                response[RESPONSE] = 400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                clients.remove(client)
                client.close()
            return
        # Если обычное сообщение
        elif ACTION in message and message[ACTION] == MSG and \
                TIME in message and MSG_TEXT in message and \
                SENDER in message and DESTINATION in message:
            message_list.append(message)
            return
        # Если сообщение о выходе клиента
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            return
        else:
            log.warning('Принято некорректное сообщение от клиента.')
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            })
            return

    @Log()
    def process_message(self, message, names, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь-сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        :param message:
        :param names:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            send_message(names[message[DESTINATION]], message)
            log.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                     f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            log.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

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

        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        names = dict()

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
            err_lst = []

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
                                                messages, client_with_message, clients, names)
                    except:
                        log.info(f'Клиент {client_with_message.getpeername()} '
                                 f'отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for i in messages:
                try:
                    self.process_message(i, names, send_data_lst)
                except Exception:
                    log.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()


if __name__ == '__main__':
    new_server = Server()
    Server.main(new_server)
