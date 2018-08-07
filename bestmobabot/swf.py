from __future__ import annotations

import logging
import sys
import warnings
from enum import IntEnum
from gzip import GzipFile
from io import BytesIO
from lzma import LZMAFile
from struct import Struct
from typing import Any, BinaryIO, Iterable, Tuple

import click
import requests

from bestmobabot.constants import HEROES_SWF_URL
from bestmobabot.logging_ import install_logging, logger

ui8 = Struct('<B')
ui16 = Struct('<h')
ui32 = Struct('<I')


class Signature(IntEnum):
    UNCOMPRESSED = ord('F')
    ZLIB = ord('C')
    LZMA = ord('Z')


def read_swf(io: BinaryIO):
    signature, version, file_length = read_header(io)
    logger.debug(f'SWF v{version} {signature.name} ({file_length} bytes).')

    if signature == Signature.LZMA:
        # https://stackoverflow.com/a/39777419/359730
        read_value(io, ui32)  # compressed length
        io = LZMAFile(BytesIO(io.read(5) + 8 * b'\xff' + io.read()))
    elif signature == Signature.ZLIB:
        io = GzipFile(fileobj=io)

    x_min, _, y_min, _ = read_rect(io)
    assert x_min == y_min == 0, (x_min, y_min)
    read_value(io, ui16)  # frame rate
    read_value(io, ui16)  # frame count

    read_tags(io)


def read_header(io: BinaryIO) -> Tuple[Signature, int, int]:
    signature = Signature(read_value(io, ui8))
    assert read_value(io, ui8) == ord('W')
    assert read_value(io, ui8) == ord('S')
    version: int = read_value(io, ui8)
    file_length: int = read_value(io, ui32)
    return signature, version, file_length


def read_tags(io: BinaryIO):
    while True:
        try:
            code_length: int = read_value(io, ui16)
        except StopIteration:
            break
        type_ = code_length >> 6
        tag_length = code_length & 0b111111
        if tag_length == 0x3F:
            # Long tag header.
            tag_length: int = read_value(io, ui32)
        logger.debug(f'Type {type_}: length: {tag_length}')
        if type_ == 82:
            read_do_abc(io, tag_length)
        else:
            # Skip unknown tag.
            io.read(tag_length)


def read_do_abc(io: BinaryIO, tag_length: int):
    io = BytesIO(io.read(tag_length))
    read_value(io, ui32)  # flags
    logger.info(f'Name: {read_string(io)}.')
    print(read_value(io, ui16), read_value(io, ui16))


def read_string(io: BinaryIO) -> str:
    return bytes(read_until(io, 0)).decode('utf-8')


def read_until(io: BinaryIO, sentinel: int) -> Iterable[int]:
    while True:
        byte, = io.read(1)
        if byte == sentinel:
            break
        yield byte


def read_rect(io: BinaryIO) -> Tuple[int, int, int, int]:
    bits = read_bits(io)
    n_bits = read_ub(bits, 5)
    x_min = read_sb(bits, n_bits)
    x_max = read_sb(bits, n_bits)
    y_min = read_sb(bits, n_bits)
    y_max = read_sb(bits, n_bits)
    return x_min, x_max, y_min, y_max


def read_sb(bits: Iterable[int], n_bits: int) -> int:
    return expand_sign(read_ub(bits, n_bits), n_bits)


def read_ub(bits: Iterable[int], n_bits: int) -> int:
    return pack_bits(take_bits(n_bits, bits))


def expand_sign(value: int, n_bits: int) -> int:
    # https://stackoverflow.com/a/32031543/359730
    sign_bit = 1 << (n_bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def read_bits(io: BinaryIO) -> Iterable[int]:
    while True:
        byte, = io.read(1)  # type: int
        yield from ((byte >> i) & 1 for i in range(7, -1, -1))


def pack_bits(bits: Iterable[int]) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def take_bits(n_bits: int, bits: Iterable[int]) -> Iterable[int]:
    return (bit for _, bit in zip(range(n_bits), bits))


def read_struct(io: BinaryIO, struct: Struct) -> Any:
    bytes_ = io.read(struct.size)
    if not bytes_:
        raise StopIteration
    return struct.unpack(bytes_)


def read_value(io: BinaryIO, struct: Struct) -> Any:
    value, = read_struct(io, struct)
    return value


@click.command()
def main():
    install_logging(logging.DEBUG, sys.stderr)
    if not sys.warnoptions:
        warnings.simplefilter('ignore')

    logger.info('Downloading SWF…')
    with requests.get(HEROES_SWF_URL) as response:
        response.raise_for_status()
        content = response.content
        logger.info(f'Downloaded {len(content)} bytes.')

    logger.info('Parsing SWF…')
    read_swf(BytesIO(content))


if __name__ == '__main__':
    main()
