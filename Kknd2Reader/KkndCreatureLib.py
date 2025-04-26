
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

class LibraryEntry:
    Id : int
    Name : str

class CreatureLibrary:

    MAGIC_FILE = 0x4B32434C
    MAGIC_ENTRY = 0x4B324352
    MAGIC_BMP = 0x424D

    def ReadLibraryFile(self, fileName : str) -> None:

        with open(fileName, "rb") as file:
            data = file.read()

        self.__ParseLibraryData(data)

    @staticmethod
    def __ParseLibraryData(data : bytes) -> None:
        magic = int.from_bytes(data[0 : 4])
        if magic != CreatureLibrary.MAGIC_FILE:
            raise Exception("missing magic number at file start")
        
        numberOfEntries = int.from_bytes(data[4 : 6], "little")
        pos = 6

        for _ in range(numberOfEntries):
            entry, pos = CreatureLibrary.__ParseEntry(data, pos)

    @staticmethod
    def __ParsePascalString(data : bytes, position : int) -> tuple[str, int]:
        length = data[position]
        position += 1
        b = data[position : position + length]
        position += length
        s = b.decode("ascii")
        return s, position
    
    @staticmethod
    def __ParseEntry(data : bytes, pos : int) -> tuple[LibraryEntry, int]:

        magic = int.from_bytes(data[pos : pos + 4])
        if magic != CreatureLibrary.MAGIC_ENTRY:
            raise Exception(f"missing magic number at entry start (position {pos})")
        pos += 4
        
        libraryEntry = LibraryEntry()

        libraryEntry.Id = int.from_bytes(data[pos : pos + 2], "little")
        pos += 2

        libraryEntry.Name, pos = CreatureLibrary.__ParsePascalString(data, pos)
        print(libraryEntry.Name)

        lengthMetadata = int.from_bytes(data[pos : pos + 2], "little")
        pos += 2 + lengthMetadata + 6

        numberOfProperties = int.from_bytes(data[pos : pos + 2], "little")
        pos += 2

        for _ in range(numberOfProperties):
            pos = CreatureLibrary.__ParseProperty(data, pos)

        hasBmpFile = int.from_bytes(data[pos : pos + 1])
        pos += 1

        if hasBmpFile != 0:
            pos = CreatureLibrary.__ParseBitmap(data, pos)

        return libraryEntry, pos

    @staticmethod
    def __ParseBitmap(data : bytes, pos : int) -> int:
        # it is a normal BMP file
        magic = int.from_bytes(data[pos : pos + 2])
        if magic != CreatureLibrary.MAGIC_BMP:
            raise Exception(f"missing magic number at BMP start (position {pos})")

        fileSize = int.from_bytes(data[pos + 2 : pos + 6], "little")

        bmpImageData = data[pos : pos + fileSize]

        pos += fileSize

        return pos

    @staticmethod
    def __ParseProperty(data : bytes, pos : int) -> int:

        name, pos = CreatureLibrary.__ParsePascalString(data, pos)

        propertyType = int.from_bytes(data[pos : pos + 1])
        pos += 1

        if propertyType in (1, 2, 3):
            pos += 12
            arrayLength = int.from_bytes(data[pos : pos + 2], "little")
            pos += 2

            for _ in range(arrayLength):
                arrayItemName, pos = CreatureLibrary.__ParsePascalString(data, pos)
                arrayItemValue = int.from_bytes(data[pos : pos + 4], "little")
                pos += 4

        else:
            pos += 14
        
        return pos
    


