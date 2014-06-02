from hexahexacontadecimal import ParsimoniousEncoder

__author__ = 'Danny Goodall'
import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_base62_implementation(self):
        p = ParsimoniousEncoder(additional_encoding="")
        test_results = [
            (0,'0'),
            (1,'1'),
            (61,'z'),
            (62,'10'),
            (63,'11'),
            (24543263,'1eyp5'),
            (302231454903657293676544,'1Vg3hltyXNOOy8'),
            (707364294219318078921,'DannyGoodall')
        ]
        for inp,expected in test_results:
            r = p.encode_from_int(inp)
            self.assertEqual(
                r,
                expected,
                msg=u'Encode: {} == {}'.format(r,expected)
            )
            r = p.decode_to_int(expected)
            self.assertEqual(
                r,
                inp,
                msg=u'Decode: {} == {}'.format(r,expected)
            )


    def test_zero_fill_base62(self):
        p = ParsimoniousEncoder(additional_encoding="",zero_fill_mask="~~~~~~")
        test_results = [
            (0,'~~~~~0'),
            (1,'~~~~~1'),
            (61,'~~~~~z'),
            (62,'~~~~10'),
            (63,'~~~~11'),
            (24543263,'~1eyp5'),
            (302231454903657293676544,'1Vg3hltyXNOOy8'),
            (707364294219318078921,'DannyGoodall')
        ]
        for inp,expected in test_results:
            r = p.encode_from_int(inp)
            self.assertEqual(
                r,
                expected,
                msg=u'Encode: {} == {}'.format(r,expected)
            )
            r = p.decode_to_int(expected)
            self.assertEqual(
                r,
                inp,
                msg=u'Decode: {} == {}'.format(r,expected)
            )


    def test_zero_fill_base62_fail(self):
        p = ParsimoniousEncoder(additional_encoding="",zero_fill_mask="~~~~~~",enforce_zero_fill_length=True)
        test_results = [
            (302231454903657293676544,'1Vg3hltyXNOOy8'),
            (707364294219318078921,'DannyGoodall')
        ]
        for inp,expected in test_results:
            with self.assertRaises(ValueError):
                r = p.encode_from_int(inp)


    def test_base66_implementation(self):
        p = ParsimoniousEncoder(additional_encoding="-_.~")
        test_results = [
            (0, '0'),
            (1, '1'),
            (65, '~'),
            (66, '10'),
            (67, '11'),
            (24543263,'1JONf'),
            (302231454903657293676544,'iFsGUkO.0tsxw'),
            (1403275513540316837237,'DannyGoodall')
        ]
        for inp, expected in test_results:
            r = p.encode_from_int(inp)
            self.assertEqual(
                r,
                expected,
                msg=u'Encode: {} == {}'.format(r,expected)
            )
            r = p.decode_to_int(expected)
            self.assertEqual(
                r,
                inp,
                msg=u'Decode: {} == {}'.format(r,expected)
            )


if __name__ == "__main__":
    unittest.main()