import unittest
from dabepg.xml import marshall, unmarshall

class Test(unittest.TestCase):

    def test_parse_serviceinfo(self):
        si = unmarshall(open('test/SI.xml'))
        print si
        print marshall(si, indent='    ')


if __name__ == "__main__":
    unittest.main()