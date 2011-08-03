import unittest
from dabepg.xml import marshall, unmarshall

class Test(unittest.TestCase):

    def test_parse_serviceinfo(self):
        pi = unmarshall(open('test/PI.xml'))
        print pi
        print marshall(pi, indent='    ')


if __name__ == "__main__":
    unittest.main()