# -*- coding: utf-8 -*-

from KkndFileCompression import UncompressFile
from KkndFileContainer import ReadFileTypeList, ContainerFile
import KkndFileMobd as _mobd

import os
from pathlib import Path

# KKND2 file endings:
#   ".lpk"  Spritesheet container
#   ".bpk"  Image container
#   ".spk"  Sound set
#   ".lps"  Singleplayer map
#   ".lpm"  Multiplayer map
#   ".mpk"  Matrix set (destroyable map part, tile replacements)

def ShowFileContent(fileName : str, contentJsonFileName : str | None = None) -> None:
    """ Shows the content of a KKND2 asset file.#

    Args:
        fileName (str): The KKND2 asset file and path.
        contentJsonFileName (str | None, optional): A JSON file with additional informations about the content of the asset file. Defaults to None.
    """

    print("********************************************************************************")
    print(f"Read file {fileName}")

    data, version, timestamp = UncompressFile(fileName)

    print(f"data len = {len(data)} version = {version} timestamp = {timestamp}")

    fileTypeList, fileTypeListOffset = ReadFileTypeList(data, contentJsonFileName)
    print(f"File type list offset: {fileTypeListOffset}")

    for fileType in fileTypeList:
        print(f"File type: index {fileType.Index} type {fileType.FileType} file list offset {fileType.FileListOffset}")

        for file in fileType.FileList:
            print(f"    File: index = {file.Index} file offset = {file.FileOffset} file length = {file.FileLength} name = {file.FileName}")

def ShowContentOfFilesInDirectory(directoryPath : str, fileEnding : str | None = None) -> None:
    """ Shows the content of all KKND2 asset files in a directory.

    Args:
        directoryPath (str): The directory.
        fileEnding (str | None, optional): Show only the content of files with this file name ending. Defaults to None.
    """

    for dir in os.scandir(directoryPath):
        if not dir.is_dir():
            continue

        for file in os.scandir(dir):
            if not file.is_file():
                continue
            
            if (fileEnding is not None) and (not file.path.endswith(fileEnding)):
                continue

            #print(file.path)
            ShowFileContent(file.path)

def ExportFile(containerFileName : str, fileTypeIndex : int, fileIndex : int) -> None:
    """ Exports the raw data of a file in the KKND2 asset container.

    Args:
        containerFileName (str): The name and path of the KKND2 asset file.
        fileTypeIndex (int): Export the file with this file type index.
        fileIndex (int): Export the file with this index.
    """
    containerData, _, _ = UncompressFile(containerFileName)
    fileTypeList, _ = ReadFileTypeList(containerData)
    file = fileTypeList[fileTypeIndex].GetFile(fileIndex)

    with open(f"{Path(containerFileName).stem}_{fileTypeIndex}_{fileIndex}.mobd", "wb") as f:
        f.write(file.RawData)

def ExportContainerFiles(containerFileName : str, fileTypeStr : str, outDir : str) -> None:
    """ Export all files of a KKND2 asset file container.

    Args:
        containerFileName (str): The name and path of the KKND2 asset file.
        fileTypeStr (str): Export the files with this file type.
        outDir (str): The output directory.
    """
    containerData, _, _ = UncompressFile(containerFileName)
    fileTypeList, _ = ReadFileTypeList(containerData)

    for fileType in fileTypeList:
        if fileType.FileType != fileTypeStr:
            continue

        for file in fileType.FileList:
            with open(f"{outDir}/{Path(containerFileName).stem}_{file.Index}.mobd", "wb") as f:
                f.write(file.RawData)

def ExportAllMobdFiles(directoryPath : str, outDir : str) -> None:
    """ Export all MOBD files to a directory.

    Args:
        directoryPath (str): The directory with the MOBD fils.
        outDir (str): The output directory.
    """
    for dir in os.scandir(directoryPath):
        if not dir.is_dir():
            continue

        for file in os.scandir(dir):
            if (not file.is_file()) or (not file.path.endswith(".lpk")):
                continue
            
            ExportContainerFiles(file.path, "MOBD", outDir)

def TestMobdAnimation(file : ContainerFile) -> None:
    """ Only for testing: read an animation.

    Args:
        file (ContainerFile): The container with the animation.
    """
    print(f"*** FILE Number {file.FileNumber} Index {file.Index} ***")
    mobd = _mobd.MobdFile()
    mobd.ReadAnimations(file.RawData, file.FileOffset)

def TestMobd(containerFileName : str, fileTypeStr : str, fileIndex : int | None = None) -> None:
    """ Only for testing: read an MOBD File.

    Args:
        containerFileName (str): The name and path of the KKND2 asset file.
        fileTypeStr (str): Export the files with this file type.
        fileIndex (int | None, optional): _description_. Defaults to None.
    """
    containerData, _, _ = UncompressFile(containerFileName)
    fileTypeList, _ = ReadFileTypeList(containerData)

    for fileType in fileTypeList:
        if fileType.FileType == fileTypeStr:
            
            if fileIndex is None:
                for file in fileType.FileList:
                    TestMobdAnimation(file)
            else:
                TestMobdAnimation(fileType.FileList[fileIndex])

            break

def TestMobdDir(directoryPath : str, fileEnding : str | None = None) -> None:
    """ Only for testing: 

    Args:
        directoryPath (str): _description_
        fileEnding (str | None, optional): _description_. Defaults to None.
    """
    for dir in os.scandir(directoryPath):
        if not dir.is_dir():
            continue

        for file in os.scandir(dir):
            if not file.is_file():
                continue
            
            if (fileEnding is not None) and (not file.path.endswith(fileEnding)):
                continue

            print("******************************************")
            print(f"********** {file.path} **********")

            TestMobd(file.path, "MOBD")

if __name__ == "__main__":
    
    # ShowContentOfFilesInDirectory("assets", ".lpk")

    # ExportAllMobdFiles("assets", "out")

    # ShowFileContent("assets/spritesheets/gamesprt.lpk") # , "gamesprt.lpk.json")
    # ShowFileContent("assets/spritesheets/gamesprt.lpk")
    # ShowFileContent("assets/spritesheets/gluesprt.lpk")

    # Multiplayer Map
    ShowFileContent("assets/multiplayermap/mlti_01.lpm")
    # ShowFileContent("assets/singleplayermap/robo_01.lps")

    # Tile sets
    # ExportFile("assets/spritesheets/gluesprt.lpk", 2)
    # ShowFileContent("assets/spritesheets/gamesprt.lpk")
    # ExportFile("assets/spritesheets/gamesprt.lpk", 10)

    # TestMobd("assets/spritesheets/gamesprt.lpk", "MOBD", 1)
    # TestMobd("assets/spritesheets/gamesprt.lpk", "MOBD", 52)
    # TestMobd("assets/spritesheets/gamesprt.lpk", "MOBD")
    # TestMobdDir("assets", ".lpk")




