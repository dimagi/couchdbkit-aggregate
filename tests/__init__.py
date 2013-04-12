import unittest
from couchdbkit.client import Server
from couchdbkit.consumer import Consumer

class CouchdbkitTestCase(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self._delete_db()
        self.db = self.server.create_db("couchdbkit_test")
        self.consumer = Consumer(self.db)

    def tearDown(self):
        self._delete_db()

    def _delete_db(self):
        try:
            del self.server['couchdbkit_test']
        except:
            pass
