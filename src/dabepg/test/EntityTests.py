import unittest

from dabepg import ContentId

class ContentIdTest(unittest.TestCase):

    def test_parse_contentid(self):
        print ContentId.fromstring('e1.ce15.c221.0.1')
        print ContentId.fromstring('e1.c586')   


if __name__ == "__main__":
    unittest.main()