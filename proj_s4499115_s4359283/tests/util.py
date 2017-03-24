import unittest


class DNSTestCase(unittest.TestCase):
    def inequalityException(self, o1, o2, msg):
        new_msg = str(o1) + " != " + str(o2)
        if msg:
            new_msg += " : " + msg
        return self.failureException(new_msg)
