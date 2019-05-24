import unittest

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from boa.io import (
    inflate,
    deflate,
)
from boa.object import (
    newInteger,
    newString,
    TRUE,
    FALSE,
    NULL,
)

class TestIO(unittest.TestCase):
    def test_constantIO(self):
        vals = [
            newInteger(5),
            newInteger(10),
            newInteger(-10000),
            TRUE,
            FALSE,
            NULL,
            newString("abc def"),
            newString("this is a \nstring"),
        ]

        for val in vals:
            deflated = deflate(val)
            inflated = inflate(deflated)
            self.assertEqual(val.objectType, inflated.objectType)
            self.assertEqual(val.inspect(), inflated.inspect())

if __name__ == '__main__':
    unittest.main()
