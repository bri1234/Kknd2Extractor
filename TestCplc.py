
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

from Kknd2Reader.KkndFileCompression import UncompressFile
from Kknd2Reader.KkndFileContainer import ReadFileTypeList
from Kknd2Reader.KkndFileCplc import CplcFile
from Kknd2Reader.KkndCreatureLib import CreatureLibrary

creatureLibrary = CreatureLibrary()
creatureLibrary.ReadLibraryFile("assets/creature.klb")

cplcFileList : list[CplcFile] = []

data, _, _ = UncompressFile("assets/multiplayermap/mlti_07.lpm")
# data, _, _ = UncompressFile("assets/singleplayermap/robo_03.lps")

fileTypeList, _ = ReadFileTypeList(data)
for fileType in fileTypeList:
    if fileType.FileType != "CPLC":
        continue
    
    for file in fileType.FileList:
        cplcFile = CplcFile(creatureLibrary)
        cplcFile.ReadCplcFile(file.RawData, file.FileOffset)
        cplcFileList.append(cplcFile)

print(len(cplcFileList))

for entity in cplcFileList[0].EntityList:
    print(f"Type: {entity.Id} Name: {entity.Name} X={entity.X} Y={entity.Y}")


