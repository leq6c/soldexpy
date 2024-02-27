import re

from construct import (
    Bit,
    BitsSwapped,
    BitStruct,
    Bytes,
    BytesInteger,
    Int8ul,
    Int64ul,
    Padding,
)


def convert_camel_case_to_snake_case(name: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", name).lower()


def preprocess_key(key: str) -> str:
    return convert_camel_case_to_snake_case(key)


def u8(key: str):
    key = preprocess_key(key)
    return key / Int8ul


def u64(key: str):
    key = preprocess_key(key)
    return key / Int64ul


def u128(key: str):
    key = preprocess_key(key)
    # unsigned, little endian
    return key / BytesInteger(16, False, True)


def publicKey(key: str):
    key = preprocess_key(key)
    return key / Bytes(32)


def pad(key: str, length: int):
    key = preprocess_key(key)
    return key / Padding(length)


def blob(key: str, length: int):
    key = preprocess_key(key)
    return key / Bytes(length)


class WideBitsBuilder:
    def __init__(self, property_name: str, len=64):
        self.property_name = property_name
        self.fields = []
        self.len = len

    def add_boolean(self, key: str):
        key = preprocess_key(key)
        assert len(self.fields) < self.len
        self.fields.append(key / Bit)

    def get_layout(self):
        return self.property_name / BitsSwapped(
            BitStruct(*self.fields + [Padding(self.len - len(self.fields))])
        )
