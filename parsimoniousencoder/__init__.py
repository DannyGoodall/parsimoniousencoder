# !/usr/bin/env python
# -*- coding: utf8 -*-

"""Encoding of numbers to short strings. Based on code by Alexander Ljunberg

https://github.com/aljungberg/hexahexacontadecimal

"""

from io import StringIO
import urllib


class ParsimoniousEncoder(object):
    """Based on Alexander Ljunberg's hexahexacontadecimal encoding. This however allows the encoding to
    ignore certain characters if they don't work for a given content, and for the resultant encoded string
    to be 'zero'-filled so that sort order can be maintained.
    """

    BASE62_ALPHABET = u"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    HEXAHEXACONTADECIMAL_ADDITIONS = u"-_.~"
    BASE_66_ALPHABET = BASE62_ALPHABET + HEXAHEXACONTADECIMAL_ADDITIONS

    def __init__(self, additional_encoding="", zero_fill_mask='',enforce_zero_fill_length=False):

        self.base_alphabet = ParsimoniousEncoder.BASE62_ALPHABET + additional_encoding

        # Do we want the resultant encoding to be 'zero' filled?
        if (zero_fill_mask):
            if not isinstance(zero_fill_mask, basestring) or \
                            len(zero_fill_mask) < 2 or \
                            len(set(zero_fill_mask)) > 1:
                raise ValueError(
                    u"zero_fill should be at least 2 chars long, containing a repeated single character.".format(
                        self.base_alphabet))
            # Remove the zero_fill char from our base alphabet
            self.base_alphabet = self.base_alphabet.replace(zero_fill_mask[0], '')

        # Workout the mask to use for zero filling
        self.zero_fill_mask = zero_fill_mask

        #Compute the base
        self.base = len(self.base_alphabet)

        # Should we raise a ValueError if the 'zero' filled result is longer than the mask?
        #   If no, then a result longer than the mask can be returned.
        self.enforce_zero_fill_length = enforce_zero_fill_length


    def explain(self):
        return u"Numbers encoded using base: {}\n  From an alphabet of: {}\n  Padding fill: {}".format(
            self.base,
            self.base_alphabet,
            self.zero_fill_mask
        )


    def encode_from_int(self, n):
        """

            :param n: Number to encode
            :return: The encoded version of the number

            >>> p = ParsimoniousEncoder(additional_encoding="-_.~") # Results in a base 66 encoder
            >>> p.encode_from_int(0)
            '0'
            >>> p.encode_from_int(1)
            '1'
            >>> p.encode_from_int(65)
            '~'
            >>> p.encode_from_int(66)
            '10'
            >>> p = ParsimoniousEncoder(additional_encoding="") # Results in a base 62 encode
            >>> p.encode_from_int(61)
            'z'
            >>> p.encode_from_int(62)
            '10'
            >>> hexahexacontadecimal_encode_int(302231454903657293676544)
            'iFsGUkO.0tsxw'
            """

        if n == 0:
            result = self.base_alphabet[0].encode('ascii')
        else:
            r = StringIO()
            while n:
                n, t = divmod(n, self.base)
                r.write(self.base_alphabet[t])
            result = r.getvalue().encode('ascii')[::-1]

        return self._zero_fill_pad(result)


    def _zero_fill_pad(self, value):
        if not self.zero_fill_mask:
            return value

        if len(value)>len(self.zero_fill_mask) and self.enforce_zero_fill_length:
            raise ValueError("The value is longer than the zero-fill mask")

        # Return the right had n chars of the combined strings
        #  Where n is the longer of the zero-fill mask or the value string
        length = max(len(self.zero_fill_mask),len(value))

        return (self.zero_fill_mask + value)[-length:]


    def _zero_fill_removal(self, value):
        return value if not self.zero_fill_mask else value.replace(self.zero_fill_mask[0], '')


    def decode_to_int(self, s):
        """Parse a number expressed in hexahexacontadecimal as an integer (or long).
            >>> hexahexacontadecimal_decode_int('0')
            0
            >>> hexahexacontadecimal_decode_int('1')
            1
            >>> hexahexacontadecimal_decode_int('~')
            65
            >>> hexahexacontadecimal_decode_int('10')
            66
            >>> hexahexacontadecimal_decode_int('11')
            67
            >>> hexahexacontadecimal_decode_int('iFsGUkO.0tsxw')
            302231454903657293676544L
            """

        n = 0
        for c in self._zero_fill_removal(s):
            n = n * self.base + self.base_alphabet.index(c)

        return n


"""Hexahexacontadecimal is a compact format to express a number in a URL. It uses all characters allowed in
a URL without escaping -- the [unreserved characters](http://tools.ietf.org/html/rfc3986#section-2.3) --
making it the shortest possible way to express an integer in a URL.

Note that `urllib.quote` [escapes the tilde character (~)](http://bugs.python.org/issue16285), which is
not necessary as of RFC3986.

### Hexahexacontadecimal vs Base 64 in URLs

    >>> n = 292231454903657293676544
    >>> import base64
    >>> urlquote(base64.urlsafe_b64encode(long_to_binary(n)))
    'PeHmHzZFTcAAAA%3D%3D'
    >>> urlquote(hexahexacontadecimal_encode_int(n))
    'gpE4Xoy7fw5AO'

Worst case scenario for plain Base 64:

    >>> n = 64 ** 5 + 1
    >>> urlquote(base64.urlsafe_b64encode(long_to_binary(n)))
    'QAAAAQ%3D%3D'
    >>> urlquote(hexahexacontadecimal_encode_int(n))
    'ucrDZ'

Worst case for hexahexacontadecimal:

    >>> n = 66 ** 5 + 1
    >>> urlquote(base64.urlsafe_b64encode(long_to_binary(n)))
    'SqUUIQ%3D%3D'
    >>> urlquote(hexahexacontadecimal_encode_int(n))
    '100001'

That big SHA-512 you always wanted to write in a URL:

    >>> n = 2 ** 512
    >>> urlquote(base64.urlsafe_b64encode(long_to_binary(n)))
    'AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%3D'
    >>> urlquote(hexahexacontadecimal_encode_int(n))
    'JK84xqGD9FMXPNubPghADlRhBUzlqRscC2h~8xmi99PvuQsUCIB2CHGhMUQR8FLm72.Hbbctkqi89xspay~y4'

Massive savings.

### Are the savings really significant?

If you're currently doing your BASE64 encoding the naive way, then yes:

    >>> sum(len(urlquote(base64.urlsafe_b64encode(long_to_binary(n)))) for n in xrange(10 ** 5))
    531584
    >>> sum(len(urlquote(hexahexacontadecimal_encode_int(n))) for n in xrange(10 ** 5))
    295578

### But what if I use Base64 without padding?

Then the savings are not as significant. But it's still an improvement. Using the code from [this StackOverFlow question](http://stackoverflow.com/a/561704/76900):

    >>> from hexahexacontadecimal.num_encode_base64 import num_encode as num_encode_base64
    >>> n = 64 ** 5 + 1
    >>> urlquote(num_encode_base64(n))
    'BAAAAB'
    >>> urlquote(hexahexacontadecimal_encode_int(n))
    'ucrDZ'
    >>> n = 66 ** 5 + 1
    >>> urlquote(num_encode_base64(n))
    'BKpRQh'
    >>> urlquote(hexahexacontadecimal_encode_int(n))
    '100001'
    >>> n = 2 ** 512
    >>> urlquote(num_encode_base64(n))
    'EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    >>> urlquote(hexahexacontadecimal_encode_int(n))
    'JK84xqGD9FMXPNubPghADlRhBUzlqRscC2h~8xmi99PvuQsUCIB2CHGhMUQR8FLm72.Hbbctkqi89xspay~y4'
    >>> sum(len(urlquote(num_encode_base64(n))) for n in xrange(10 ** 5))
    295840
    >>> sum(len(urlquote(hexahexacontadecimal_encode_int(n))) for n in xrange(10 ** 5))
    295578

Why settle for less than perfect?

"""

BASE66_ALPHABET = u"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.~"
BASE = len(BASE66_ALPHABET)


def urlquote(s, safe=None):
    """Like urllib.quote() but don't escape ~, in accordance with RFC3986."""

    return urllib.quote(s, safe='~' + (safe or ''))


def long_to_binary(n):
    """Take an integer and write it as a binary string.

    >>> long_to_binary(0)
    '\\x00'
    >>> long_to_binary(255)
    '\\xff'
    >>> long_to_binary(512 + 3)
    '\\x02\\x03'
    """

    h = '%x' % n
    return ('0' * (len(h) % 2) + h).decode('hex')


def binary_to_long(b):
    """Take a binary string and read it as an integer.

    >>> binary_to_long('\\x00')
    0
    >>> binary_to_long('\\xff')
    255
    >>> binary_to_long('\\x02\\x03')
    515
    """

    return int(b.encode('hex'), 16)


def hexahexacontadecimal_encode_int(n):
    """Represent a number in hexahexacontadecimal, a compact format of unreserved URL characters.

    >>> hexahexacontadecimal_encode_int(0)
    '0'
    >>> hexahexacontadecimal_encode_int(1)
    '1'
    >>> hexahexacontadecimal_encode_int(65)
    '~'
    >>> hexahexacontadecimal_encode_int(66)
    '10'
    >>> hexahexacontadecimal_encode_int(67)
    '11'
    >>> hexahexacontadecimal_encode_int(302231454903657293676544)
    'iFsGUkO.0tsxw'

    """

    if n == 0:
        return BASE66_ALPHABET[0].encode('ascii')

    r = StringIO()
    while n:
        n, t = divmod(n, BASE)
        r.write(BASE66_ALPHABET[t])
    return r.getvalue().encode('ascii')[::-1]


def hexahexacontadecimal_decode_int(s):
    """Parse a number expressed in hexahexacontadecimal as an integer (or long).

    >>> hexahexacontadecimal_decode_int('0')
    0
    >>> hexahexacontadecimal_decode_int('1')
    1
    >>> hexahexacontadecimal_decode_int('~')
    65
    >>> hexahexacontadecimal_decode_int('10')
    66
    >>> hexahexacontadecimal_decode_int('11')
    67
    >>> hexahexacontadecimal_decode_int('iFsGUkO.0tsxw')
    302231454903657293676544L

    """

    n = 0
    for c in s:
        n = n * BASE + BASE66_ALPHABET.index(c)

    return n


def main():
    p = ParsimoniousEncoder(additional_encoding="-_.~")  # Results in a base 66 encoder
    print "Base 66"
    print p.encode_from_int(0)
    print p.encode_from_int(1)
    print p.encode_from_int(65)
    print p.encode_from_int(66)

    p = ParsimoniousEncoder(additional_encoding="")  # Results in a base 62 encode
    print "Base 62"
    print p.encode_from_int(61)
    print p.encode_from_int(62)
    print p.encode_from_int(302231454903657293676544)

    p = ParsimoniousEncoder(additional_encoding="", zero_fill_mask="~~~~~~")  # Results in a base 61 encode
    print "Base 62 (Zero-filled)"
    print p.encode_from_int(0)
    print p.encode_from_int(1)
    print p.encode_from_int(60)
    print p.encode_from_int(61)
    print p.encode_from_int(62)
    print p.encode_from_int(302231454903657293676544)
    print p.encode_from_int(707364294219318078921)

    p = ParsimoniousEncoder(additional_encoding="", zero_fill_mask="~~~~~~", enforce_zero_fill_length=True)  # Results in a base 61 encode
    print "Base 62 (Zero-filled)"
    print p.encode_from_int(0)
    print p.encode_from_int(1)
    print p.encode_from_int(60)
    print p.encode_from_int(61)
    print p.encode_from_int(62)
    try:
        print p.encode_from_int(302231454903657293676544)
    except ValueError:
        print "Failed as expected"
    try:
        print p.encode_from_int(707364294219318078921)
    except ValueError:
        print "Failed as expected"

if __name__ == "__main__":
    main()
