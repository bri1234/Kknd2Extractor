# -*- coding: utf-8 -*-

from io import BufferedReader
import struct

def ReadInt32LE(file : BufferedReader) -> int:
    """ Reads a 32 bit signed integer (little endian) from a file.

    Args:
        file (BufferedReader): the file to be read from.

    Returns:
        int: The number.
    """
    return struct.unpack("<i", file.read(4))[0]

def ReadInt32BE(file : BufferedReader) -> int:
    """ Reads a 32 bit signed integer (big endian) from a file.

    Args:
        file (BufferedReader): the file to be read from.
        bigEndian (bool, optional): Big endian yes or no. Defaults to False.

    Returns:
        int: The number.
    """
    return struct.unpack(">i", file.read(4))[0]

def ReadUInt32LE(file : BufferedReader) -> int:
    """ Reads a 32 bit unsigned integer (little endian) from a file.

    Args:
        file (BufferedReader): the file to be read from.
        bigEndian (bool, optional): Big endian yes or no. Defaults to False.

    Returns:
        int: The number.
    """
    return struct.unpack("<I", file.read(4))[0]

def ReadUInt32BE(file : BufferedReader) -> int:
    """ Reads a 32 bit unsigned integer (big endian) from a file.

    Args:
        file (BufferedReader): the file to be read from.
        bigEndian (bool, optional): Big endian yes or no. Defaults to False.

    Returns:
        int: The number.
    """
    return struct.unpack(">I", file.read(4))[0]

def GetInt16LE(data : bytearray, index : int) -> int:
    """ Reads a 16 bit signed integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from("<h", data, index)[0]

def GetInt16BE(data : bytearray, index : int) -> int:
    """ Reads a 16 bit signed integer (big endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from(">h", data, index)[0]

def GetUInt16LE(data : bytearray, index : int) -> int:
    """ Reads a 16 bit unsigned integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from("<H", data, index)[0]

def GetUInt16BE(data : bytearray, index : int) -> int:
    """ Reads a 16 bit unsigned integer (big endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from(">H", data, index)[0]

def GetInt32LE(data : bytearray, index : int) -> int:
    """ Reads a 32 bit signed integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from("<i", data, index)[0]

def GetInt32BE(data : bytearray, index : int) -> int:
    """ Reads a 32 bit signed integer (big endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from(">i", data, index)[0]

def GetUInt32LE(data : bytearray, index : int) -> int:
    """ Reads a 32 bit unsigned integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from("<I", data, index)[0]

def GetUInt32BE(data : bytearray, index : int) -> int:
    """ Reads a 32 bit unsigned integer (big endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return struct.unpack_from(">I", data, index)[0]

def GetString(data : bytearray, index : int, length : int) -> str:
    """ Reads a string from a data buffer.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the string starts.
        length (int): The length of the string in bytes.

    Returns:
        str: The string.
    """

    dataStr = data[index : index + length]
    return dataStr.decode("ASCII")

def GetStringReverse(data : bytearray, index : int, length : int) -> str:
    """ Reads a string reverse from a data buffer.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the string starts.
        length (int): The length of the string in bytes.

    Returns:
        str: The string.
    """

    dataStr = data[index : index + length]
    dataStr.reverse()
    return dataStr.decode("ASCII")

