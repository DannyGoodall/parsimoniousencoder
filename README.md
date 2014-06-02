A ParsimoniousEncoder
=====================

**Parsimonious Encoder is a fork of Alexander Ljunberg's hexahexacontadecimal - which he describes as "the most compact 
way to encode a number into a URL".**

My need was different and instead of using the compact encoding of a long Long number to build a url-safe reference, 
I needed to use the resultant encoding as a key for a MongoDB collection. It turns out (after much head scratching) 
that MongoDB cannot use all of the characters in hexahexacontadecimal. The 
```
.
-
_
```
chars all seem to cause a problem.  As a result I needed a way to limit the characters used, to the onces that MongoDB is happy with. 

In addition, I needed to be able to reliably sort these encoded keys. For example in base 62, encoding of the following 
numbers is sequential, but from an ascii sort perspective the order is wrong:
```
61 -> 'z'
62 -> '10'
```
and Python will evaluate these as so: 
```python
>>> 'z' > '10'
True
```
To allow these encoded values to be compared, I've implemented a 'zero-fill' feature. It ensures that encoded results 
are the same length and are padded upfront with a character that is ignored by the encoding routines.
```
60 -> '00000z'
61 -> '000011'
```
Which means that the Python comparison now works:
```python
>>> '00000z' > '000010'
False
```
**NOTE: that in using the zero in this way, it is not available for the encoding alphabet - hence the encoding effectively
becomes base 61**.

## Usage ##

```python
ParsimoniusEncoder(additional_encoding="",zero_fill_mask="", enforce_zero_fill_length=Falue)
```
By default the ParsimoniousEncoder is setup to use a base 62 encoding using the following characters (the base alphabet):
```
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```
To increase the base of the encoding, additional encodings can be supplied on the additional_encoding parameter, 
such that 
```python
additional_encoding="-_.~"
```
Will result in the base 66 version of [Alexander Ljunberg's](https://github.com/aljungberg) original [hexahexacontadecimal](https://github.com/aljungberg/hexahexacontadecimal) implementation. The additional_encodings could, in future versions, allow for a bunch on additional Unicode characters to be used to further increase the base of the encoding. But using Unicode characters hasn't been tested yet.

The zero_fill_mask parameter can be used to create encodings that can be compared with each other to correctly determine their ordering. **As mentioned aboive, if the character used for the fill mask is contained in the base alphabet, it will be removed from the base alphabet - thus reducing the effective base of the encoding. For example:
```python
p = ParsimoniousEncoder(zero_fill_mask="000000")
```
Would result in a zero-padded encoding - to six characters, but the encoding base will now be 61 as the 0 is no longer able to be used as part of the encoding alphabet.

Any character can be used for the zero_fill_mask.

The enforce_zero_fill_length parameter determines whether, if the resultant encoding is longer than the supplied zero_fill_mask, a ValueError is raised. By default, enforce_zero_fill_length is False which means that encodings longer than the supplied zero_fill_mask are returned. With enforce_zero_fill_length set to True, then any encoding which is longer than the supplied zero_fill_mask will raise an exception.

## Examples

```python
from parsimoniousencoder import ParsimoniousEncoder
p = ParsimoniousEncoder(additional_encoding="-_.~")  # Results in a base 66 encoder
print "Base 66"
print p.encode_from_int(0)  # Results in '0'
print p.encode_from_int(1)  # Results in '1'
print p.encode_from_int(65) # Results in '~'
print p.encode_from_int(66) # Results in '10'

p = ParsimoniousEncoder(additional_encoding="")  # Results in a base 62 encode
print "Base 62"
print p.encode_from_int(61)  # Results in 'z'
print p.encode_from_int(62)  # Results in '10'
print p.encode_from_int(302231454903657293676544)  # Results in '1Vg3hltyXNOOy8'

p = ParsimoniousEncoder(additional_encoding="", zero_fill_mask="000000")  # Results in a base 61 encode
print "Base 62 (Zero-filled)"
print p.encode_from_int(0)  # Results in '000001' - (The 0 has been removed from the encoding alphabet as it is in the mask)
print p.encode_from_int(1)  # Results in '000002'
print p.encode_from_int(60) # Results in '00000z'
print p.encode_from_int(61) # Results in '000021'
print p.encode_from_int(62) # Results in '000022'
print p.encode_from_int(302231454903657293676544) # Results in '2rrdHGQLtWcYOS'
print p.encode_from_int(707364294219318078921) # Results in 'HGckpRySNak5'

p = ParsimoniousEncoder(additional_encoding="", zero_fill_mask="000000", enforce_zero_fill_length=True)  # Results in a base 61 encode
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
```

## License ##

Free to use and modify under the terms of the BSD open source license.

## Author ##

Danny Goodall
__Based on work by Alexander Ljungberg__
