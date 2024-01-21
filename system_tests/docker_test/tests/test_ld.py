import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
from helpers import update_late_day_deduction

class TestLD(unittest.TestCase):

    @weight(0)
    @number("1.0")
    def test_get_ld(self):
        """
        Running late day test...
        """
        print('Returning: ', update_late_day_deduction())

