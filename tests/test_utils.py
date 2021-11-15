"""Unit-тесты утилит"""

import sys
import os
import unittest
import json
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import get_message, send_message, validate_ip, validate_port
sys.path.append(os.path.join(os.getcwd(), '..'))


class FakeSocket:
    '''
    Класс-заглушка для имитации работы сокетов.
    '''

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def recv(self, max_package_length):
        """Имитация метода recv сокета"""
        test_message = json.dumps(self.test_dict)
        return test_message.encode(ENCODING)

    def send(self, message):
        """Имитация метода send сокета"""
        test_message = json.dumps(self.test_dict)
        # кодируем сообщение для дальнейшего сравнения
        self.encoded_message = test_message.encode(ENCODING)
        # сохраняем сообщение из сокета
        self.received_message = message


class UtilsTests(unittest.TestCase):
    '''
    Класс с тестами
    '''

    def setUp(self) -> None:
        """Объявляем переменные"""
        self.err_dict = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
        self.ok_dict = {RESPONSE: 200}
        self.send_dict = {
            ACTION: PRESENCE,
            TIME: 42.42,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

    def test_get_message(self):
        """Приём сообщения"""
        # Создаём тестовые сокеты:
        ok_socket = FakeSocket(self.ok_dict)
        err_socket = FakeSocket(self.err_dict)

        self.assertEqual(get_message(ok_socket), self.ok_dict)
        self.assertEqual(get_message(err_socket), self.err_dict)

    def test_send_message(self):
        """Отправка сообщения"""
        # Создаём тестовый сокет:
        send_socket = FakeSocket(self.send_dict)

        send_message(send_socket, self.send_dict)
        self.assertEqual(send_socket.encoded_message, send_socket.received_message)

        self.assertRaises(Exception, send_message, send_socket, b'test_message')

    def test_validate_ip_len(self):
        """Тест вызова исключения при IP-адресе неправильной длины"""
        self.assertRaises(ValueError, validate_ip, '192.168.0')

    def test_validate_ip_digit(self):
        """Тест вызова исключения при IP-адресе не из цифр"""
        self.assertRaises(ValueError, validate_ip, '192.168.0.O')

    def test_validate_ip_0_255(self):
        """Тест вызова исключения при IP-адресе c некорректными числами"""
        self.assertRaises(ValueError, validate_ip, '192.168.0.666')

    def test_validate_port(self):
        """Тест вызова исключения при некорректном значении порта"""
        self.assertRaises(ValueError, validate_port, 80)


if __name__ == '__main__':
    unittest.main()
