import struct
from abc import abstractmethod


def get_image_size(file):
    if isinstance(file, str):
        file = open(file, "rb")
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    data = file.read(26)

    for format_class in ImageFormat.__subclasses__():
        if format_class.detect(file, size, data):
            return format_class(file, size, data)

    raise Exception("Unknown Image Format")


class ImageFormat(object):
    def __init__(self, file, size, data):
        self.file = file
        self.size = size
        self.data = data
        self.dimensions = (None, None)

    @staticmethod
    def detect(file, size, data):
        return NotImplemented

    @abstractmethod
    def parse(self):
        return NotImplemented

    def get_dimensions(self):
        if self.dimensions == (None, None):
            self.parse()
        return self.dimensions

    def __repr__(self):
        if self.dimensions == (None, None):
            return "{}(not evaluated)".format(self.__class__.__name__, *self.dimensions)
        return "{}(x={}, y={}, file={}, buffer={})".format(
            self.__class__.__name__, self.dimensions[0], self.dimensions[1], self.file.name, len(self.data)
        )


class WebPFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        return size >= 24 and data.startswith(b"RIFF") and data[8:12] == b"WEBP"

    def parse(self):
        data = self.data
        file = self.file
        byte_count = struct.unpack("<I", data[16:20])  # noqa: F841
        if self.data[12:16] == b"VP8L":
            a, b, c, d = struct.unpack("4B", data[21:25])
            width = 1 + (((b & 0b111) << 8) | a)
            height = 1 + (((d & 0b1) << 10) | (c << 2) | ((b & 0b11000000) >> 6))
        elif data[12:16] == b"VP8 ":
            sc_a, sc_b, sc_c = struct.unpack("3B", data[23:26])
            if sc_a != 0x9D or sc_b != 0x01 or sc_c != 0x2A:
                raise Exception("Missing start code block for lossy WebP image")
            width, height = struct.unpack("<HH", file.read(4))
        elif data[12:16] == b"VP8X":
            width, height = struct.unpack("<HxH", data[24:] + file.read(3))
            width, height = width + 1, height + 1
        self.dimensions = (int(width), int(height))


class FlifFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        return size >= 16 and data.startswith(b"FLIF")

    def read_varint(self, data):
        VALUE_MASK = 0b01111111
        LEADING_BIT_MASK = 0b10000000

        values = []
        for byte in data:
            value = byte & VALUE_MASK
            has_leading_bit = byte & LEADING_BIT_MASK
            values.append(value)
            if not has_leading_bit:
                break

        size, result = 0, 0
        for i, val in enumerate(values[::-1]):
            size += 1
            result |= val << (i * 7)

        return result, size

    def parse(self):
        data = self.data
        meta = struct.unpack("1B", data[4:5])[0]
        channels = meta >> 4  # noqa: F841
        img_format = meta & 0x0F  # noqa: F841
        bytes_per_channel = struct.unpack("1B", data[5:6])[0]  # noqa: F841
        width, size = self.read_varint(data[6:])
        height, size = self.read_varint(data[6 + size :])
        self.dimensions = (int(width + 1), int(height + 1))


class PngFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        return size >= 24 and data[1:4] == b"PNG" and data[12:16] == b"IHDR"

    def parse(self):
        data = self.data
        width, height = struct.unpack(">LL", data[16:24])
        self.dimensions = (int(width), int(height))


class GifFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        return size >= 10 and data[:6] in (b"GIF87a", b"GIF89a")

    def parse(self):
        data = self.data
        width, height = struct.unpack("<HH", data[6:10])
        self.dimensions = (int(width), int(height))


class JpgFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        return size >= 2 and data.startswith(b"\377\330")

    def parse(self):
        file = self.file
        file.seek(0)
        file.read(2)
        b = file.read(1)
        while b and ord(b) != 0xDA:
            while ord(b) != 0xFF:
                b = file.read(1)
            while ord(b) == 0xFF:
                b = file.read(1)
            if ord(b) >= 0xC0 and ord(b) <= 0xC3:
                file.read(3)
                height, width = struct.unpack(">HH", file.read(4))
                break
            else:
                file.read(int(struct.unpack(">H", file.read(2))[0]) - 2)
            b = file.read(1)
        self.dimensions = (int(width), int(height))


class BmpFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        return size >= 26 and data[0:2] == b"BM"

    def parse(self):
        data = self.data
        headersize = struct.unpack("<I", data[14:18])[0]
        if headersize == 12:
            width, height = struct.unpack("<HH", data[18:22])
        elif headersize >= 40:
            width, height = struct.unpack("<ii", data[18:26])
            height = abs(height)  # height is inverted, so abs() the result
        self.dimensions = (int(width), int(height))


class TiffFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        return size >= 8 and data[:4] in (b"II\052\000", b"MM\000\052")

    def parse(self):
        file = self.file
        data = self.data
        byteOrder = data[:2]
        boChar = ">" if byteOrder == "MM" else "<"
        tiffTypes = {
            1: (1, boChar + "B"),
            2: (1, boChar + "c"),
            3: (2, boChar + "H"),
            4: (4, boChar + "L"),
            5: (8, boChar + "LL"),
            6: (1, boChar + "b"),
            7: (1, boChar + "c"),
            8: (2, boChar + "h"),
            9: (4, boChar + "l"),
            10: (8, boChar + "ll"),
            11: (4, boChar + "f"),
            12: (8, boChar + "d"),
        }
        ifdOffset = struct.unpack(boChar + "L", data[4:8])[0]
        countSize = 2
        file.seek(ifdOffset)
        ec = file.read(countSize)
        ifdEntryCount = struct.unpack(boChar + "H", ec)[0]
        ifdEntrySize = 12
        width, height = -1, -1
        for i in range(ifdEntryCount):
            entryOffset = ifdOffset + countSize + i * ifdEntrySize
            file.seek(entryOffset)
            tag = file.read(2)
            tag = struct.unpack(boChar + "H", tag)[0]
            if tag == 256 or tag == 257:
                type = file.read(2)
                type = struct.unpack(boChar + "H", type)[0]
                if type not in tiffTypes:
                    raise Exception("Unkown Image Format")
                typeSize = tiffTypes[type][0]
                typeChar = tiffTypes[type][1]
                file.seek(entryOffset + 8)
                value = file.read(typeSize)
                value = int(struct.unpack(typeChar, value)[0])
                if tag == 256:
                    width = value
                else:
                    height = value
            if width > -1 and height > -1:
                break
        self.dimensions = (int(width), int(height))


class IcoFormat(ImageFormat):
    @staticmethod
    def detect(file, size, data):
        reserved = struct.unpack("<H", data[:2])[0]
        ico_type = struct.unpack("<H", data[2:4])[0]  # 1 is for "icon", 2 is for "cursor"
        return size >= 2 and reserved == 0 and ico_type == 1

    def parse(self):
        data = self.data
        # read the dimensions of the first image
        width = ord(str(data[6]))
        height = ord(str(data[7]))
        self.dimensions = (int(width), int(height))
