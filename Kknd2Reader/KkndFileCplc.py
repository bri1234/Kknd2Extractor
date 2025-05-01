
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

from .DataBuffer import GetUInt32LE, GetUInt8
from .KkndCreatureLib import CreatureLibrary
from Kknd2Reader.KkndFileCompression import UncompressFile
from Kknd2Reader.KkndFileContainer import ReadFileTypeList
import wx # type: ignore

class CplcEntity:
    """ Represents one entity of the KKND2 map.
    """

    # the ID
    Id : int

    # true if the entity is not always visible on the map, e.g. tech bunkers
    IsOptional : bool

    # the name
    Name : str

    # the X coordinate in pixels
    X : int

    # the Y coordinate in pixels
    Y : int

    # the entity image
    Image : wx.Image | None

class CplcFile:
    """ A CPLC file in a KKND2 file container stores the unit data of a KKND2 map.
    """

    __creatureLib : CreatureLibrary | None

    # list of all entities on the map
    EntityList : list[CplcEntity]

    def __init__(self, creatureLibrary : CreatureLibrary | None) -> None:
        self.__creatureLib = creatureLibrary
        self.EntityList = []
        
    def ReadCplcFile(self, fileData : bytearray, fileOffset : int) -> None:
        """ Reads the CPLC file data that contains the units and buildings on the map.

        Args:
            fileData (bytearray): The CPLC raw data.
            fileOffset (int): The offset of the CPLC file in the file container.
        """
        self.EntityList = []

        entityPointer = GetUInt32LE(fileData, 4)
        while entityPointer != 0:
            entityPos = entityPointer - fileOffset

            entity = self.__ParseEntity(fileData, entityPos)
            self.EntityList.append(entity)

            entityPointer = GetUInt32LE(fileData, entityPos + 16)

    def __ParseEntity(self, fileData : bytearray, entityPos : int) -> CplcEntity:
        """ Parses the entity from the raw data.

        Args:
            fileData (bytearray): The CPLC raw data.
            entityPos (int): The real position of the entity in the raw file data.

        Returns:
            CplcEntity: The entity.
        """

        entity = CplcEntity()

        entity.Id = GetUInt8(fileData, entityPos)

        if self.__creatureLib is not None:
            if entity.Id not in self.__creatureLib.EntryList:
                raise Exception(f"Unknown entity with Id {entity.Id}")
            
            creatureLibEntry = self.__creatureLib.EntryList[entity.Id]
            entity.IsOptional = creatureLibEntry.IsOptional
            entity.Name = creatureLibEntry.Name
            entity.Image = creatureLibEntry.Image
        else:
            entity.IsOptional = False
            entity.Name = ""
            entity.Image = None

        entity.X = GetUInt32LE(fileData, entityPos + 5)
        entity.Y = GetUInt32LE(fileData, entityPos + 9)
        
        return entity

def ReadCplcFile(fileName : str, creatureLibrary : CreatureLibrary | None) -> CplcFile:
    """ Reads the CPLC file from a KKND2 asset file container.

    Args:
        fileName (str): The name of the KNND2 asset file.

    Returns:
        CplcFile: The CPLC file.
    """

    data, _, _ = UncompressFile(fileName)

    fileTypeList, _ = ReadFileTypeList(data)
    for fileType in fileTypeList:
        if fileType.FileType != "CPLC":
            continue
        
        for file in fileType.FileList:
            cplcFile = CplcFile(creatureLibrary)
            cplcFile.ReadCplcFile(file.RawData, file.FileOffset)

            return cplcFile

    raise Exception(f"No CPLC file found in file container {fileName}")


