import unittest
import logging

__author__ = 'aganezov'


class MockingLoggingHandler(logging.Handler):
    def __init__(self,  *args, **kwargs):
        self.messages = {
            'DEBUG': [],
            'INFO': [],
            'WARNING': [],
            'ERROR': [],
            'CRITICAL': []
        }
        super(MockingLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        self.acquire()
        try:
            self.messages[record.levelname].append(record.getMessage())
        finally:
            self.release()

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                message_list.clear()
        finally:
            self.release()

if __name__ == '__main__':
    unittest.main()
