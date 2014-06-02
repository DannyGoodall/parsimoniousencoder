A ParsimoniousEncoder
=====================

**Parsimonious Encoder is a fork of Alexander Ljunberg's hexahexacontadecimal - which he describes as "the most compact 
way to encode a number into a URL".**

My need was different and instead of using the compact encoding of a long Long number, I needed to use the resultant 
encoding as a key for a MongoDB collection. It turns out (after much head scratching) that MongoDB cannot use all of 
the characters in hexahexacontadecimal. The chars (.-_), all seem to cause a problem. As a result I needed a way to 
limit the characters used, to the onces that MongoDB is happy with. 

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

MORE TO FOLLOW:

## License

Free to use and modify under the terms of the BSD open source license.

## Author

Danny Goodall
__Base on work by Alexander Ljungberg__
