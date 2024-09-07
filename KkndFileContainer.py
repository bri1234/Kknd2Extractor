# -*- coding: utf-8 -*-

import json
from DataBuffer import GetUInt32LE, GetString

class ContainerFile:
    """ This class represents one raw file in the file container.
    """

    Index : int             # index of the file (some files can be missing)
    FileNumber : int        # index of the file (consecutive number)
    FileType : str          # type of file, e.g. MOBD

    FileOffset : int        # the offset of the corresponding file list
    FileLength : int        # length of the file in bytes

    RawData : bytearray     # the raw file data
    
    FileName : str          # Name of the file (optional)
    
    def __init__(self, fileNumber : int, index : int, fileType : str) -> None:
        self.FileNumber = fileNumber
        self.Index = index
        self.FileType = fileType

        self.FileOffset = 0
        self.FileLength = 0
        self.FileLength = 0
        self.FileName = ""

class ContainerFileType:
    """ This class represents one file type in the file container.
        The file type holds the list of files of this type.
    """

    Index : int                 # index of the file type
    FileType : str              # the file type
    FileListOffset : int        # the offset of the corresponding file list

    FileList : list[ContainerFile]  # list of files of this file type

    def __init__(self, index : int, fileType : str, fileListOffset : int) -> None:
        self.Index = index
        self.FileType = fileType
        self.FileListOffset = fileListOffset
        self.FileList = []

    def GetFile(self, fileIndex : int) -> ContainerFile:
        for file in self.FileList:
            if file.Index == fileIndex:
                return file
        
        raise Exception(f"File with index {fileIndex} not found!")

def ReadFileTypeList(data : bytearray, tableOfContentsJsonFileName : str | None = None) -> tuple[list[ContainerFileType], int]:
    """ Reads the content of the raw file container data and returns a list of file types and files.

    Args:
        data (bytearray): The raw file container data.
        tableOfContentsJsonFileName (str | None): An optional JSON file that contains the file names of the files in the container.

    Returns:
        tuple[list[AssetFileType], int]: List of file types, offset of the file type list in raw data.
    """

    fileTypeList : list[ContainerFileType] = []

    # get the offset of the file type list
    fileTypeListOffset = GetUInt32LE(data, 0)
    
    fileTypeIndex = 0
    while True:
        # get file type and file list offset
        pos = fileTypeListOffset + fileTypeIndex * 8
        fileTypeStr = GetString(data, pos, 4)
        fileListOffset = GetUInt32LE(data, pos + 4)

        # end of file type list reached?
        if fileListOffset == 0:
            break
        
        fileType = ContainerFileType(fileTypeIndex, fileTypeStr, fileListOffset)
        fileTypeList.append(fileType)

        fileTypeIndex += 1

    # get the offset of the first file lists
    firstFileListOffset = fileTypeListOffset
    for fileType in fileTypeList:
        if fileType.FileListOffset < firstFileListOffset:
            firstFileListOffset = fileType.FileListOffset

    # read file lists for each file type
    for idx in range(len(fileTypeList)):
        fileListOffset = fileTypeList[idx].FileListOffset
        fileTypeStr = fileTypeList[idx].FileType

        if idx < len(fileTypeList) - 1:
            fileListLength = fileTypeList[idx + 1].FileListOffset - fileListOffset
        else:
            fileListLength = fileTypeListOffset - fileListOffset
        
        fileList = __ReadFileList(data, fileTypeStr, fileListOffset, fileListLength, firstFileListOffset)
        fileTypeList[idx].FileList = fileList

    # give every file a readable name if possible
    if tableOfContentsJsonFileName is not None:
        __AddFileNameToFiles(tableOfContentsJsonFileName, fileTypeList)

    return fileTypeList, fileTypeListOffset

def __ReadFileList(data : bytearray, fileType : str, fileListOffset : int, fileListLength : int, firstFileListOffset : int) -> list[ContainerFile]:
    """ Reads the contents of a file list.

    Args:
        data (bytearray): The raw data.
        fileListOffset (int): The offset of the file list.
        fileListLength (int): The length of the file list.
        firstFileListOffset (int): The first offset of all file lists.

    Returns:
        list[AssetFile]: List of files.
    """
    fileList : list[ContainerFile] = []

    if fileListLength % 4 != 0:
        raise Exception(f"Can not read file list: invalid length: {fileListLength}")
    
    # read the offset of each file
    fileNumber = 0
    for index in range(fileListLength // 4):
        fileOffset = GetUInt32LE(data, fileListOffset + index * 4)

        # was the file removed?
        if fileOffset == 0:
            continue

        file = ContainerFile(fileNumber, index, fileType)
        file.FileOffset = fileOffset
        fileList.append(file)
        fileNumber += 1

    # calculate the file length of each file
    for idx in range(len(fileList)):
        if idx < len(fileList) - 1:
            fileLength = fileList[idx + 1].FileOffset - fileList[idx].FileOffset
        else:
            fileLength = firstFileListOffset - fileList[idx].FileOffset
        
        fileList[idx].FileLength = fileLength

    # copy the file data from the buffer
    for file in fileList:
        file.RawData = data[file.FileOffset : file.FileOffset + file.FileLength]

    return fileList

def __AddFileNameToFiles(tableOfContentsJsonFileName : str, fileTypeList : list[ContainerFileType]) -> None:
    """ Reads a JSON file with the description of the contents of the file container.

    Args:
        tableOfContentsJsonFileName (str): The name of the JSON file with the description of the contents of the container.
        fileTypeList (list[ContainerFileType]): The file type list of the container.
    """

    with open(tableOfContentsJsonFileName) as f:
        tableOfContents = json.load(f)

    if tableOfContents is None:
        raise Exception(f"Can not open file {tableOfContentsJsonFileName}")

    for fileType in fileTypeList:

        # search the file type 
        for fileTypeDesc in tableOfContents["FileTypes"]:
            if fileTypeDesc["Type"] == fileType.FileType:
                __AddFileNameToFileList(fileTypeDesc["Files"], fileType.FileList)
                break

def __AddFileNameToFileList(fileListDesc : list[dict[str, str | int]], fileList : list[ContainerFile]) -> None:
    """ Adds the filename to the files in the list.

    Args:
        fileListToc (list[dict[str, str  |  int]]): List with the file description.
        fileList (list[ContainerFile]): List of files.
    """

    for file in fileList:
        for fileDesc in fileListDesc:

            if file.Index == fileDesc["Index"]:
                file.FileName = str(fileDesc["Name"])
                break
    