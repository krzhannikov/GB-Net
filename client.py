"""Клиентская часть"""

import sys
import json
import socket
import time
import argparse
import threading
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, SENDER, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MSG, MSG_TEXT, DESTINATION, EXIT
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
    def message_from_server(self, sock, my_username):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = get_message(sock)
                if ACTION in message and message[ACTION] == MSG and \
                        SENDER in message and DESTINATION in message \
                        and MSG_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MSG_TEXT]}')
                    log.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                f'\n{message[MSG_TEXT]}')
                else:
                    log.error(f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                log.critical(f'Потеряно соединение с сервером.')
                break

    @Log()
    def create_message(self, sock, account_name='Guest'):
        """Функция запрашивает адресата и текст сообщения и возвращает его.
        Также завершает работу при вводе подобной команды
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки или \'quit\' для завершения работы: ')
        if message == 'quit':
            sock.close()
            log.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            ACTION: MSG,
            TIME: time.time(),
            SENDER: account_name,
            DESTINATION: to_user,
            MSG_TEXT: message
        }
        log.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(sock, message_dict)
            log.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            log.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @Log()
    def user_interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        print(f'Ваше имя пользователя: {username}')
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                send_message(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                log.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @Log()
    def print_help(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    @Log()
    def create_exit_message(self, account_name):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    @Log()
    def arg_parser(self):
        """Парсер аргументов коммандной строки"""
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-n', '--name', default=None, nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = namespace.port
        client_name = namespace.name

        # валидация аргументов
        # client.py 192.168.88.254 4242 -m listen
        validate_port(server_port)
        validate_ip(server_address)

        return server_address, server_port, client_name

    @Log()
    def main(self):
        """Загружаем параметы коммандной строки"""
        server_address, server_port, client_name = self.arg_parser()

        # Запрашиваем имя пользователя, если не было указано в аргументах
        if not client_name:
            client_name = input('Введите имя пользователя: ')

        log.info(
            f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
            f'порт: {server_port}, имя пользователя: {client_name}')

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
            # Если соединение с сервером установлено корректно,
            # запускаем клиенский процесс приёма сообщний
            receiver = threading.Thread(target=self.message_from_server, args=(transport, client_name))
            receiver.daemon = True
            receiver.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем.
            user_interface = threading.Thread(target=self.user_interactive, args=(transport, client_name))
            user_interface.daemon = True
            user_interface.start()
            log.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение или пользователь
            # ввёл exit. Поскольку все события обработываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    new_client = Client()
    Client.main(new_client)
