
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

from .KkndCreatureLib import CreatureLibrary

class CplcEntity:
    Id : int
    Name : str
    X : int
    Y : int

class CplcFile:

    __creatureLib : CreatureLibrary

    EntityList : list[CplcEntity]

    def __init__(self, creatureLibrary : CreatureLibrary) -> None:
        self.__creatureLib = creatureLibrary
        self.EntityList = []
        
    def ReadCplcFile(self, fileData : bytearray, fileOffset : int) -> None:
        
        self.EntityList = []

        entityPointer = int.from_bytes(fileData[4 : 8], 'little')
        while entityPointer != 0:
            entityPos = entityPointer - fileOffset

            entity = self.__ParseEntity(fileData, entityPos)
            self.EntityList.append(entity)

            entityPointer = int.from_bytes(fileData[entityPos + 16 : entityPos + 20], 'little')

    def __ParseEntity(self, fileData : bytearray, entityPos : int) -> CplcEntity:

        entity = CplcEntity()

        entity.Id = int.from_bytes(fileData[entityPos : entityPos + 1])

        if entity.Id in self.__creatureLib.EntryList:
            entity.Name = self.__creatureLib.EntryList[entity.Id].Name
        else:
            entity.Name = "???"

        entity.X = int.from_bytes(fileData[entityPos + 5 : entityPos + 9], 'little')
        entity.Y = int.from_bytes(fileData[entityPos + 9 : entityPos + 13], 'little')
        
        return entity

