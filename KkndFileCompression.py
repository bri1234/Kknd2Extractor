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
from DataBuffer import ReadUInt32LE, ReadUInt32BE

def __ReadHeader(file : BufferedReader) -> tuple[int, int, int, int]:
    """ Reads the header of the file.

    Args:
        file (BufferedReader): The file to be read from.

    Returns:
        tuple[int, int, int, int]: uncompressed size, RRLC size, version, timestamp
    """
    version = ReadUInt32LE(file)
    timestamp = ReadUInt32LE(file)
    uncompressedSize = ReadUInt32BE(file)
    rrlcSize = ReadUInt32LE(file) # compressed size ???

    return uncompressedSize, rrlcSize, version, timestamp

def __ReadUncompressedData(file : BufferedReader, uncompressedData : bytearray, size : int) -> None:
    """ Reads a chunk of uncompressed data.

    Args:
        file (BufferedReader): The file to be read from.
        uncompressedData (bytearray): To stored the data.
        size (int): Number of bytes to read.

    Raises:
        Exception: if not enough data could be read.

    """
    data = file.read(size)
    
    if len(data) != size:
        raise Exception(f"Can not uncompress body: can nor read {size} bytes! (got {len(data)})")
    
    uncompressedData.extend(data)

def __ReadCompressedData(file : BufferedReader, uncompressedData : bytearray, compressedSize : int, uncompressedSize : int) -> None:
    """ Uncompress a chunk of data.

    Args:
        file (BufferedReader): The file to be read from.
        compressedSize (int): The compressed size.
        uncompressedSize (int): The uncompressed size.

    Returns:
        bytearray: The uncompressed data.
    """
    startNumBytesUncompressedData = len(uncompressedData)
    numBytesRead = 0

    while numBytesRead < compressedSize:

        bitMasks = file.read(2)
        numBytesRead += 2

        for bitIdx in range(16):

            if (bitMasks[bitIdx // 8] & (1 << (bitIdx % 8))) == 0:
                uncompressedData.extend(file.read(1))
                numBytesRead += 1
            
            else:

                metaBytes = file.read(2)
                numBytesRead += 2

                readSize = 1 + (metaBytes[0] & 0x000F)
                readOffset = ((metaBytes[0] & 0x00F0) << 4) | metaBytes[1]
                substitutes = bytearray(readSize)
                dataEndIdx = len(uncompressedData)

                for idx in range(readSize):
                    dataIdx = dataEndIdx - readOffset + idx % readOffset
                    substitutes[idx] = uncompressedData[dataIdx]

                uncompressedData.extend(substitutes)

            if numBytesRead >= compressedSize:
                break
    
    if numBytesRead != compressedSize:
        raise Exception(f"Can not uncompress body: number of bytes read != compressed size!")
    
    if len(uncompressedData) - startNumBytesUncompressedData != uncompressedSize:
        raise Exception(f"Can not uncompress body: size of uncompressed data != uncompressed size!")

def __UncompressBody(file : BufferedReader, uncompressedData : bytearray, uncompressedSize : int) -> None:
    """ Uncompress the body data.

    Args:
        file (BufferedReader): The file to be read from.
        uncompressedSize (int): The uncompressed size.

    Returns:
        bytearray: The uncompressed data.
    """

    while len(uncompressedData) < uncompressedSize:
        chunkUncompressedSize = ReadUInt32LE(file)
        chunkCompressedSize = ReadUInt32LE(file)

        if chunkCompressedSize == chunkUncompressedSize:
            __ReadUncompressedData(file, uncompressedData, chunkCompressedSize)
        else:
            __ReadCompressedData(file, uncompressedData, chunkCompressedSize, chunkUncompressedSize)

def UncompressFile(fileName : str) -> tuple[bytearray, int, int]:
    """ Reads a compressed file and returns the uncompressed data.

    Args:
        fileName (str): The name of the file to read.

    Returns:
        bytearray, version: The uncompressed data and version number.
    """
    uncompressedData = bytearray()

    with open(fileName, "rb") as file:

        uncompressedSize, _, version, timestamp = __ReadHeader(file)

        __UncompressBody(file, uncompressedData, uncompressedSize)

    if len(uncompressedData) != uncompressedSize:
        raise Exception(f"Can not uncompress file: size of uncompressed data != uncompressed size ({len(uncompressedData)} != {uncompressedSize})")
    
    return uncompressedData, version, timestamp

