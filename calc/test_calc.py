import unittest
import calc


class TestCalc(unittest.TestCase):
    def test_add(self):
        self.assertEquals(calc.add(0, 0), 0)
        self.assertEquals(calc.add(0, 1), 1)
