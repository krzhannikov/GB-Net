"""Декораторы"""

import sys
import logging
import logs.confs.server_log_config
import logs.confs.client_log_config
import traceback
import inspect

# Метод определения модуля, источника запуска.
# Метод find() возвращает индекс первого вхождения искомой подстроки,
# если оно найдено в данной строке. Если не найдено - возвращает -1.
# os.path.split(sys.argv[0])[1]
if sys.argv[0].find('client') == -1:  # Ищем ключевое слово в имени модуля из которого импортировали класс Log
    # если не найден модуль client, то логируем сервер
    log = logging.getLogger('app.server')
else:
    log = logging.getLogger('app.client')


# Реализация декоратора в виде класса
class Log:
    """Класс-декоратор"""
    def __call__(self, func):
        def decorated(*args, **kwargs):
            """Обёртка"""
            res = func(*args, **kwargs)
            log.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                      f'Вызов из модуля {func.__module__}. '
                      f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
                      # stacklevel позволяет писать в лог имя модуля, который был запущен изначально, а не текущий.

                      # Альтернативный метод:
                      # f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.'
            return res
        return decorated
