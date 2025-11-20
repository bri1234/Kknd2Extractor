
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

import wx

from Kknd2Reader.KkndFileCompression import UncompressFile
from Kknd2Reader.KkndFileContainer import ReadFileTypeList, ContainerFile
from Kknd2Reader.KkndFileMobd import MobdFile, MobdFrame

def LoadSprites() -> list[ContainerFile]:
    """ Load the sprites.

    Returns:
        list[MobdFile]: List of all sprites.
    """
    containerData, _, _ = UncompressFile("assets/spritesheets/gamesprt.lpk")
    fileTypeList, _ = ReadFileTypeList(containerData, "Kknd2Reader/gamesprt.lpk.json")

    if len(fileTypeList) != 1 or fileTypeList[0].FileType != "MOBD":
        raise Exception("Unexpected file type")

    return fileTypeList[0].FileList

def ConvertColorsToPalette(colorIndexColors : dict[int, int]) -> list[int]:
    palette : list[int] = [0] * 256

    for k in colorIndexColors:
        palette[k] = colorIndexColors[k]

    return palette

def CreateColorPaletteForFrame(referenceFile : str, mobdFrame : MobdFrame) -> dict[int, int]:

    width = mobdFrame.Image.Width
    height = mobdFrame.Image.Height

    img = wx.Image()
    with open(referenceFile, "rb") as file:
        img.LoadFile(file)

    if img.GetWidth() != width or img.GetHeight() != height:
        raise Exception("invalid img size")
    
    colorIndexColors : dict[int, int] = {}
    colorIndexList : dict[int, bool] = {}

    for column in range(width):
        for row in range(height):
            if column == 25 and row == 15:
                pass

            colorIndex = mobdFrame.Image.GetPixel(column, row)
            if colorIndex == 0:
                continue
            
            colorIndexList[colorIndex] = True

            a = img.GetAlpha(column, row)
            if a == 0:
                continue

            c = (img.GetRed(column, row) << 16) | (img.GetGreen(column, row) << 8) | img.GetBlue(column, row)

            if colorIndex in colorIndexColors:
                if c != colorIndexColors[colorIndex]:
                    raise Exception(f"file '{referenceFile}' different color for color index {colorIndex} at {column},{row}: old 0x{colorIndexColors[colorIndex]:08X} new 0x{c:08X}")
            else:
                colorIndexColors[colorIndex] = c
    
    for colorIndex in colorIndexList.keys():
        if colorIndex not in colorIndexColors:
            # raise Exception(f"missing color for color index {colorIndex}")
            print(f"file '{referenceFile}' missing color for color index {colorIndex}")

    return colorIndexColors

def GetMissingColors(colors : dict[int, int], mobdFile : MobdFile) -> list[int]:

    missingColors : dict[int, bool] = {}

    for animation in mobdFile.AnimationList:
        for frame in animation.FrameList:

            width = frame.Image.Width
            height = frame.Image.Height

            for column in range(width):
                for row in range(height):

                    if column == 25 and row == 15:
                        pass

                    colorIndex = frame.Image.GetPixel(column, row)
                    if colorIndex == 0:
                        continue

                    if colorIndex not in colors:
                        missingColors[colorIndex] = True

                        # TODO: !!! print frame and animation index !!!!
                        print(f"missing color: {column}, {row}: {colorIndex}")

    return list(missingColors.keys())


def MergeColors(colorsList : list[dict[int, int]]) -> dict[int, int]:

    mergedColors : dict[int, int] = {}
    
    for colors in colorsList:
        for colorIndex in colors:
            c = colors[colorIndex]

            if colorIndex in mergedColors:
                if c != mergedColors[colorIndex]:
                    raise Exception(f"!!! different color for color index {colorIndex}: old 0x{mergedColors[colorIndex]:08X} new 0x{c:08X}")
            else:
                mergedColors[colorIndex] = c

    return mergedColors

def PrintPalette(palette : list[int]) -> None:
    print(",".join([f"0x{c:08X}" for c in palette]))
    print()

def DiffPalette(paletteRed : list[int], paletteGreen : list[int], paletteBlue : list[int]) -> None:
    for idx in range(256):
        r = paletteRed[idx]
        g = paletteGreen[idx]
        b = paletteBlue[idx]
        if r == g and r == b:
            continue

        if r != g and r != b and g != b:
            print(f"diff 3: {idx:3d} 0x{r:08X} 0x{g:08X} 0x{b:08X}")
            continue

        print(f"diff 2: {idx}")

def CreatePaletteForFrames(imgList : list[tuple[int, int]], colorName : str) -> tuple[dict[int, int], list[int]]:

    mobdFileList = LoadSprites()

    colorsList : list[dict[int, int]] = []

    for fileIdx, frameIdx in imgList:
        frame = MobdFile(mobdFileList[fileIdx]).AnimationList[frameIdx].FrameList[0]
        colors = CreateColorPaletteForFrame(f"image{fileIdx} colors {colorName}.png", frame)

        # print("--------------------------------------------------------------------")
        # print(sorted(colors.items()))

        colorsList.append(colors)

    cols = MergeColors(colorsList)

    return cols, ConvertColorsToPalette(cols)

def CheckPalette(fileIdxList : list[int], colors : dict[int, int]) -> None:
    mobdFileList = LoadSprites()

    for idx in fileIdxList:
        missingCols = GetMissingColors(colors, MobdFile(mobdFileList[idx]))

        print(f"  missing colors {idx}:")
        print("      ", end="")
        print(", ".join(str(c) for c in missingCols))

def CreatePalette() -> None:

    # imgList : list[tuple[int, int]] = [ (102, 4), (103, 4), (104, 4), (106, 5), (107, 4), (108, 5), (109, 4), (111, 4) ]
    imgList : list[tuple[int, int]] = [ (106, 5) ]

    # print("create palette red")
    # colorsRed, paletteRed = CreatePaletteForFrames(imgList, "red")

    print("create palette green")
    colorsGreen, paletteGreen = CreatePaletteForFrames(imgList, "green")

    # print("create palette blue")
    # colorsBlue, paletteBlue = CreatePaletteForFrames(imgList, "blue")

    # print("Palette red:")
    # PrintPalette(paletteRed)

    print("Palette green:")
    PrintPalette(paletteGreen)

    # print("Palette blue:")
    # PrintPalette(paletteBlue)

    # DiffPalette(paletteRed, paletteGreen, paletteBlue)

    # check palette
    # print("*** Check RED ***")
    # CheckPalette(list(range(102, 112)), colorsRed)

    print("*** Check GREEN ***")
    # CheckPalette(list(range(102, 112)), colorsGreen)
    CheckPalette(list(range(106, 107)), colorsGreen)

    # print("*** Check BLUE ***")
    # CheckPalette(list(range(102, 112)), colorsBlue)


def Main() -> None:
    CreatePalette()

if __name__ == "__main__":
    Main()
