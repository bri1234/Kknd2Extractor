# -*- coding: utf-8 -*-

import json

import KkndFileCompression as compression
import KkndFileContainer as container
# import KkndFileMobd as kkndMobd

import ExportInfantery as infantery

def Main() -> None:

    containerData, _, _ = compression.UncompressFile("assets/spritesheets/gamesprt.lpk")
    fileTypeList, _ = container.ReadFileTypeList(containerData)

    if len(fileTypeList) != 1 or fileTypeList[0].FileType != "MOBD":
        raise Exception("Unexpected file type")

    fileList = fileTypeList[0]

    data = infantery.ExportInfantery(fileList)

    with open("infantery.json", "w") as file:
        json.dump(data, file, sort_keys=True, indent=2)
    
if __name__ == "__main__":
    Main()
