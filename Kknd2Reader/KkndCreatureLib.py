
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

from .DataBuffer import GetUInt32LE, GetInt32LE, GetUInt32BE, GetUInt16LE, GetUInt16BE, GetUInt8
import math
import wx # type: ignore

MAGIC_FILE = 0x4B32434C
MAGIC_ENTRY = 0x4B324352
MAGIC_BMP = 0x424D

def ReadPascalString(data : bytes, position : int) -> tuple[str, int]:
    """ Reads a Pascal string from raw file data.

    Args:
        data (bytes): The raw data.
        position (int): The start position of the Pascal string.

    Returns:
        str: The string.
        int: The new position after the string.
    """
    length = data[position]
    position += 1

    strBytes = data[position : position + length]
    position += length

    s = strBytes.decode("ascii")
    return s, position

class LibraryEntryProperty:
    """ Represents a property of a library entry.
    """
    # the property name
    Name : str

    # the property values
    Values : dict[str, int]

    # unknown metadata
    Metadata : bytes

    def __init__(self) -> None:
        self.Values = {}

    def ReadProperty(self, data : bytes, pos : int) -> int:
        """ Reads a library entry property.

        Args:
            data (bytes): The raw library file data.
            pos (int): The property position in the file data.

        Returns:
            int: The new position after the property.
        """
        self.Name, pos = ReadPascalString(data, pos)

        propertyType = GetUInt8(data, pos)
        pos += 1

        if propertyType in (1, 2, 3):
            self.Metadata = data[pos : pos + 12]
            pos += 12

            arrayLength = GetUInt16LE(data, pos)
            pos += 2

            for _ in range(arrayLength):
                arrayItemName, pos = ReadPascalString(data, pos)
                arrayItemValue = GetUInt32LE(data, pos)
                self.Values[arrayItemName] = arrayItemValue

                pos += 4

        elif propertyType in (4, 5, 6, 7):
            pos += 14
        else:
            raise Exception(f"Unknown property type: {propertyType} of property {self.Name}")
        
        return pos
    
class LibraryEntry:
    """ Represents an entry in the creature library.
    """
    # the creature ID
    Id : int            

    # true if the entity is not always visible on the map, e.g. tech bunkers
    IsOptional : bool

    # the creature name
    Name : str          

    # the creature image
    Image : wx.Image | None

    # unknown metadata
    Metadata : bytes    

    Palette : list[int]

    def __init__(self) -> None:
        self.Palette = []

    def ReadLibraryEntry(self, data : bytes, pos : int) -> int:
        """ Reads a library entry.

        Args:
            data (bytes): The raw library file data.
            pos (int): The entry position in the file data.

        Returns:
            int: The new position after the entry.
        """

        # each library entry starts with a magic number
        magic = GetUInt32BE(data, pos)
        if magic != MAGIC_ENTRY:
            raise Exception(f"missing magic number at entry start (position {pos})")
        pos += 4

        # the entry ID
        self.Id = GetUInt8(data, pos)
        pos += 1

        self.IsOptional = GetUInt8(data, pos) != 0
        pos += 1

        # the entry Name
        self.Name, pos = ReadPascalString(data, pos)

        # unknown Metadata
        lengthMetadata = GetUInt16LE(data, pos)
        pos += 2

        self.Metadata = data[pos : pos + lengthMetadata + 6]
        pos += lengthMetadata + 6

        # number of creature properties
        numberOfProperties = GetUInt16LE(data, pos)
        pos += 2

        for _ in range(numberOfProperties):
            property = LibraryEntryProperty()
            pos = property.ReadProperty(data, pos)

        hasBmpFile = GetUInt8(data, pos)
        pos += 1

        if hasBmpFile != 0:
            pos = self.__ParseBitmap(data, pos)
        else:
            self.Image = None

        return pos

    def __ParseBitmap(self, data : bytes, pos : int) -> int:
        """ Parses the bitmap.

        Args:
            data (bytes): The raw library file data.
            pos (int): The bitmap position in the file data.

        Returns:
            int: The new position after the image.
        """
        startPos = pos

        # it is a normal BMP file
        magic = GetUInt16BE(data, pos)
        if magic != MAGIC_BMP:
            raise Exception(f"missing magic number at BMP start (position {pos})")

        fileSize = GetUInt32LE(data, pos + 2)

        # read bitmap header
        pixelDataOffset = GetUInt32LE(data, pos + 10)
        bitmapInfoHeaderSize = GetUInt32LE(data, pos + 14)
        bitmapWidth = GetUInt32LE(data, pos + 18)
        bitmapHeight = GetInt32LE(data, pos + 22)
        bitmapBitCount = GetUInt16LE(data, pos + 28)
        bitmapCompression = GetUInt32LE(data, pos + 30)
        bitmapSizeImage = GetUInt32LE(data, pos + 34)
        bitmapColorUsed = GetUInt32LE(data, pos + 46)

        pos += 54

        if bitmapColorUsed == 0:
            bitmapColorUsed = 2 ** bitmapBitCount

        bitmapRowWidthInBytes = math.ceil(bitmapWidth / 4.0) * 4

        if bitmapRowWidthInBytes * abs(bitmapHeight) != bitmapSizeImage:
            raise Exception(f"Invalid BMP bitmap size: width = {bitmapWidth} height = {bitmapHeight} bitmap size = {bitmapSizeImage}")
        
        if bitmapInfoHeaderSize != 40:
            raise Exception(f"Invalid bitmap info header size: {bitmapInfoHeaderSize}")
        
        if bitmapBitCount != 8:
            raise Exception(f"Unsupported BMP bitmap bit count: {bitmapBitCount}")
        
        if bitmapCompression != 0:
            raise Exception(f"Unsupported bitmap compression: {bitmapCompression}")
        
        # read color palette
        palette : list[int] = []

        for _ in range(bitmapColorUsed):
            colorRgb = GetUInt32LE(data, pos)
            palette.append(colorRgb)
            pos += 4
        
        self.Palette = palette
        
        if pos != startPos + pixelDataOffset:
            raise Exception(f"invalid BMP palette and header size")
        
        # read pixel data
        pixelData = data[pos : pos + bitmapSizeImage]
        imgBuffer = bytearray()
        alphaBuffer = bytearray()

        for row in range(abs(bitmapHeight)):

            r = bitmapHeight - row - 1 if bitmapHeight > 0 else row
            pixelDataRow = pixelData[r * bitmapRowWidthInBytes : (r + 1) * bitmapRowWidthInBytes]

            for column in range(bitmapWidth):
                pixel = pixelDataRow[column]

                color = palette[pixel]
                alpha = 0xFF if pixel != 0 else 0x00

                imgBuffer.append((color >> 16) & 0xFF)
                imgBuffer.append((color >> 8) & 0xFF)
                imgBuffer.append((color >> 0) & 0xFF)
                alphaBuffer.append(alpha)
        
        self.Image = wx.ImageFromBuffer(bitmapWidth, bitmapHeight, imgBuffer, alphaBuffer) # type: ignore

        pos += bitmapSizeImage

        if pos != startPos + fileSize:
            raise Exception(f"Invalid BMP file size: {fileSize}")
        
        return pos
    
class CreatureLibrary:
    """ The content of the creature library.
    """

    EntryList : dict[int, LibraryEntry]
    
    def __init__(self) -> None:
        self.EntryList = {}

    def ReadLibraryFile(self, fileName : str) -> None:
        """ Reads the content of the KKND2 creature library.

        Args:
            fileName (str): _description_
        """

        with open(fileName, "rb") as file:
            data = file.read()

        self.EntryList = self.__ReadLibraryEntries(data)

    @staticmethod
    def __ReadLibraryEntries(data : bytes) -> dict[int, LibraryEntry]:
        """ Reads the library entries

        Args:
            data (bytes): The raw file data.

        Returns:
            list[LibraryEntry]: List of all creature library entries.
        """
        # library data starts with a magic number
        magic = GetUInt32BE(data, 0)
        if magic != MAGIC_FILE:
            raise Exception("missing magic number at file start")
        
        numberOfEntries = GetUInt16LE(data, 4)
        pos = 6

        entryList : dict[int, LibraryEntry] = {}

        for _ in range(numberOfEntries):
            entry = LibraryEntry()
            pos = entry.ReadLibraryEntry(data, pos)

            entryList[entry.Id] = entry

        return entryList
    

