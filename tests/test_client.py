"""Unit-тесты клиентcкой части"""

import sys
import os
import unittest
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import Client
sys.path.append(os.path.join(os.getcwd(), '..'))


class ClientTests(unittest.TestCase):
    '''
    Класс с тестами
    '''

    def test_presence(self):
        """Тест генерации корректного запроса"""
        test = Client.create_presence(Client())
        test[TIME] = 42.42  # время приравниваем принудительно, иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 42.42, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_answer_200(self):
        """Тест корректного разбора ответа 200"""
        self.assertEqual(Client.process_ans(Client(), {RESPONSE: 200}), '200 : OK')

    def test_answer_400(self):
        """Тест корректного разбора ответа 400"""
        self.assertEqual(Client.process_ans(Client(), {RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест вызова исключения без поля RESPONSE"""
        self.assertRaises(ValueError, Client.process_ans, Client(), {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
