import unittest
import logging

__author__ = 'aganezov'


class MockingLoggingHandler(logging.Handler):
    def __init__(self,  *args, **kwargs):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': []
        }
        super(MockingLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        self.acquire()
        try:
            self.messages[record.levelnams.lower()].append(record.getMessage())
        finally:
            self.release()

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                message_list.clear()
        finally:
            self.release()


class MockingLoggingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(MockingLoggingTestCase, cls).setUpClass()
        logger = logging.getLogger()
        cls.log_handler = MockingLoggingHandler(level='DEBUG')
        logger.addHandlerRef(cls.log_handler)
        cls.log_messages = cls.log_handler.messages

    def setUp(self):
        super(MockingLoggingTestCase, self).setUp()
        self.log_handler.reset()


if __name__ == '__main__':
    unittest.main()
