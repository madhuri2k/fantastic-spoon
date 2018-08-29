import unittest
import prime_factors


class TestPrimeFactors(unittest.TestCase):
    def phanton(self):
        pass

    def test_of(self):
        self.assertEqual(prime_factors.of(1), [])
        self.assertEqual(prime_factors.of(2), [2])
        self.assertEqual(prime_factors.of(3), [3])
        self.assertEqual(prime_factors.of(4), [2, 2])
        self.assertEqual(prime_factors.of(5), [5])
        self.assertEqual(prime_factors.of(6), [2, 3])
        self.assertEqual(prime_factors.of(7), [7])
        self.assertEqual(prime_factors.of(8), [2, 2, 2])
        self.assertEqual(prime_factors.of(9), [3, 3])
        self.assertEqual(
            prime_factors.of(2 * 2 * 3 * 5 * 7 * 11 * 13),
            [2, 2, 3, 5, 7, 11, 13])


if __name__ == '__main__':
    unittest.main()
