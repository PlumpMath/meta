>>> import binascii
...
>>> @meta.Codec.register('hexlify')
... class HexlifyCodec(meta.Codec):
...     def encode(self, value, property, context):
...         return binascii.hexlify(value)
...     def decode(self, value, property, context):
...         return binascii.unhexlify(value)
...
>>> class X(meta.Entity):
...     s = meta.Bytes(codec='hexlify')
...
>>> context = meta.Context()
>>> v = X(dict(s=b'abc')).dump(context)
>>> v
{'s': b'616263'}
>>> x = X().load(v, context)
>>> x.s
b'abc'
