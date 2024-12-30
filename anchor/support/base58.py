"""
Base58 encoding adapted from the base58 package by David Keijser released under
the MIT license.

See https://github.com/keis/base58 for full credits.
"""

# 58 character alphabet used
BITCOIN_ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode_int(
    i: int, default_one: bool = True, alphabet: bytes = BITCOIN_ALPHABET
) -> bytes:
    """
    Encode an integer using Base58
    """
    if not i and default_one:
        return alphabet[0:1]
    string = b""
    base = len(alphabet)
    while i:
        i, idx = divmod(i, base)
        string = alphabet[idx : idx + 1] + string
    return string


def b58encode(v: bytes, alphabet: bytes = BITCOIN_ALPHABET) -> bytes:
    """
    Encode a string using Base58
    """

    origlen = len(v)
    v = v.lstrip(b"\0")
    newlen = len(v)

    acc = int.from_bytes(v, byteorder="big")  # first byte is most significant

    result = b58encode_int(acc, default_one=False, alphabet=alphabet)
    return alphabet[0:1] * (origlen - newlen) + result
