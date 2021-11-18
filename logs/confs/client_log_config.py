import logging
import logging.handlers
import os
from common.variables import LOG_DIR

PATH = os.path.join(LOG_DIR, 'client.log')
logger = logging.getLogger('app.client')

formatter = logging.Formatter("%(asctime)-25s %(levelname)-10s %(module)-8s %(message)s")

# Создаём файловый обработчик логирования:
fh = logging.handlers.TimedRotatingFileHandler(PATH, when='midnight', encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

# Добавляем в логгер обработчик и установим уровень логирования
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

# Отладка работы логирования
if __name__ == '__main__':
    logger.critical('Режим отладки: Критическая ошибка')
    logger.error('Режим отладки: Ошибка')
    logger.warning('Режим отладки: Предупреждение')
    logger.info('Режим отладки: Информационное сообщение')
    logger.debug('Режим отладки: Отладочная информация')
