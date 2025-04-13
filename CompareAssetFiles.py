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

def CompareAssetFiles(fileName1 : str, fileName2 : str) -> None:

    print(f"compare files {fileName1} / {fileName2}")

    data1, _, _ = UncompressFile(fileName1)
    data2, _, _ = UncompressFile(fileName2)

    print(f"data len 1 = {len(data1)} len 2 = {len(data2)}")

    fileTypeList1, _ = ReadFileTypeList(data1)
    fileTypeList2, _ = ReadFileTypeList(data2)

    if len(fileTypeList1) != len(fileTypeList2):
        raise Exception("len(fileTypeList1) != len(fileTypeList2)")
    
    for fileTypeIdx in range(len(fileTypeList1)):
        fileType1 = fileTypeList1[fileTypeIdx]
        fileType2 = fileTypeList2[fileTypeIdx]

        print()
        print("--------------------------------------------------------------------------------------------")
        print(f"File type 1: index {fileType1.Index} type {fileType1.FileType} file list offset {fileType1.FileListOffset}")
        print(f"File type 2: index {fileType2.Index} type {fileType2.FileType} file list offset {fileType2.FileListOffset}")

        if fileType1.Index != fileType2.Index or fileType1.FileType != fileType2.FileType:
            raise Exception("file type mismatch")
        
        if  fileType1.FileListOffset != fileType2.FileListOffset:
            print(f"    *** file list offset mismatch: {fileType1.FileListOffset} != {fileType2.FileListOffset}")
        
        if len(fileType1.FileList) != len(fileType2.FileList):
            raise Exception("len(fileType1.FileList) != len(fileType2.FileList)")
        
        for fileIdx in range(len(fileType1.FileList)):
            file1 = fileType1.FileList[fileIdx]
            file2 = fileType2.FileList[fileIdx]
            print()
            print(f"    File 1: index = {file1.Index} file offset = {file1.FileOffset} file length = {file1.FileLength}")
            print(f"    File 2: index = {file2.Index} file offset = {file2.FileOffset} file length = {file2.FileLength}")

            if file1.Index != file2.Index or file1.FileOffset != file2.FileOffset or file1.FileLength != file2.FileLength:
                raise Exception("file mismatch")
            
            if fileIdx == 0:
                with open(f"{fileName2}.bin", "wb") as f:
                    f.write(file2.RawData)

            # compare file length
            if len(file1.RawData) != len(file2.RawData):
                print(f"*** file length mismatch: {len(file1.RawData)} != {len(file2.RawData)}")
            
            # compare file content
            for idx in range(len(file1.RawData)):
                b1 = file1.RawData[idx]
                b2 = file2.RawData[idx]

                if b1 != b2:
                    print(f"        *** POS ${idx:06X} file 1: ${b1:02X} file 2: ${b2:02X}")

if __name__ == "__main__":

    #CompareMapdFiles("assets/TestEmpty.lpm", "assets/TestAll.lpm")
    CompareAssetFiles("assets/TestEmpty.lpm", "assets/Test_2_2.lpm")
    #CompareMapdFiles("assets/TestEmpty.lpm", "assets/Test_3_2.lpm")
    #CompareMapdFiles("assets/TestEmpty.lpm", "assets/Test_2_3.lpm")
