"""

Copyright (C) 2025  Torsten Brischalle
email: torsten@brischalle.de
web: http://www.aaabbb.de

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

from io import BufferedReader

def ReadUInt32LE(file : BufferedReader) -> int:
    """ Reads a 32 bit unsigned integer (little endian) from a file.

    Args:
        file (BufferedReader): the file to be read from.
        bigEndian (bool, optional): Big endian yes or no. Defaults to False.

    Returns:
        int: The number.
    """
    return int.from_bytes(file.read(4), byteorder='little', signed=False)

def ReadUInt32BE(file : BufferedReader) -> int:
    """ Reads a 32 bit unsigned integer (big endian) from a file.

    Args:
        file (BufferedReader): the file to be read from.
        bigEndian (bool, optional): Big endian yes or no. Defaults to False.

    Returns:
        int: The number.
    """
    return int.from_bytes(file.read(4), byteorder='big', signed=False)

def GetUInt8(data : bytearray | bytes, index : int) -> int:
    """ Reads a 8 bit unsigned integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return int.from_bytes(data[index : index + 1], signed=False)

def GetUInt16LE(data : bytearray | bytes, index : int) -> int:
    """ Reads a 16 bit unsigned integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return int.from_bytes(data[index : index + 2], byteorder='little', signed=False)

def GetUInt16BE(data : bytearray | bytes, index : int) -> int:
    """ Reads a 16 bit unsigned integer (big endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return int.from_bytes(data[index : index + 2], byteorder='big', signed=False)

def GetInt32LE(data : bytearray | bytes, index : int) -> int:
    """ Reads a 32 bit signed integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return int.from_bytes(data[index : index + 4], byteorder='little', signed=True)

def GetUInt32LE(data : bytearray | bytes, index : int) -> int:
    """ Reads a 32 bit unsigned integer (little endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return int.from_bytes(data[index : index + 4], byteorder='little', signed=False)

def GetUInt32BE(data : bytearray | bytes, index : int) -> int:
    """ Reads a 32 bit unsigned integer (big endian) from a file.

    Args:
        data (bytearray): The data buffer.
        index (int): The index where the integer starts.

    Returns:
        int: The number.
    """
    return int.from_bytes(data[index : index + 4], byteorder='big', signed=False)

def GetString(data : bytearray | bytes, index : int, length : int) -> str:
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

