
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

import collections
import os

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

def GetMostCommonColors(colorIndexColors : dict[int, list[int]]) -> dict[int, int]:

    mostCommonColorsDict : dict[int, int] = {}

    for idx in colorIndexColors:
        colorList = colorIndexColors[idx]
        colorListCnt = collections.Counter(colorList)
        mostCommonColors = colorListCnt.most_common(2)

        if (len(mostCommonColors) > 1) and (mostCommonColors[0][1] < 3 * mostCommonColors[1][1] + 10):
            print(f"color ignored: {mostCommonColors}")
            continue
        
        mostCommonColorsDict[idx] = mostCommonColors[0][0]
        pass

    return mostCommonColorsDict

def ConvertColorsToPalette(colorIndexColors : dict[int, int]) -> list[int]:
    palette : list[int] = [0] * 256

    for idx in colorIndexColors:
        palette[idx] = colorIndexColors[idx]

    return palette

def PrintPalette(palette : list[int]) -> None:
    print(",".join([f"0x{c:08X}" for c in palette]))
    print()

def CreateColorPaletteForFrame(referenceFile : str, mobdFrame : MobdFrame, colorIndexColors : dict[int, list[int]]) -> None:

    width = mobdFrame.Image.Width
    height = mobdFrame.Image.Height

    img = wx.Image()
    with open(referenceFile, "rb") as file:
        img.LoadFile(file)

    if img.GetWidth() != width or img.GetHeight() != height:
        raise Exception("invalid img size")
    
    for column in range(width):
        for row in range(height):

            colorIndex = mobdFrame.Image.GetPixel(column, row)
            if colorIndex == 0:
                continue
            
            a = int(img.GetAlpha(column, row))
            if a == 0:
                continue

            color = int((img.GetRed(column, row) << 16) | (img.GetGreen(column, row) << 8) | img.GetBlue(column, row))

            if colorIndex in colorIndexColors:
                colorIndexColors[colorIndex].append(color)
            else:
                colorIndexColors[colorIndex] = [color]
    
def CreatePaletteForFrames(imgList : list[tuple[int, int]], colorName : str) -> tuple[dict[int, list[int]], list[int]]:

    mobdFileList = LoadSprites()

    colorIndexColors : dict[int, list[int]] = {}

    for fileIdx, animationIdx in imgList:
        fileName = f"Pics/Survivors/export image{fileIdx}_{animationIdx}_0 {colorName}.png"
        if not os.path.exists(fileName):
            continue

        frame = MobdFile(mobdFileList[fileIdx]).AnimationList[animationIdx].FrameList[0]
        CreateColorPaletteForFrame(fileName, frame, colorIndexColors)
        
    print(f"number of colors: {len(colorIndexColors)}")

    mostCommonColors = GetMostCommonColors(colorIndexColors)
    palette = ConvertColorsToPalette(mostCommonColors)

    return colorIndexColors, palette

def CreatePalette() -> None:

    imgList : list[tuple[int, int]] = [ (174, 4), (174, 6), (174, 7), (175, 4), (175, 6), (175, 7), (179, 4), (179, 6), (179, 7), (180, 1), (180, 7), (180, 8), (181, 4), (181, 6), (181, 7) ]

    print("create palette red")
    colorsRed, paletteRed = CreatePaletteForFrames(imgList, "red")
    print("Palette red:")
    PrintPalette(paletteRed)

    print("create palette green")
    colorsGreen, paletteGreen = CreatePaletteForFrames(imgList, "green")
    print("Palette green:")
    PrintPalette(paletteGreen)

    print("create palette blue")
    colorsBlue, paletteBlue = CreatePaletteForFrames(imgList, "blue")
    print("Palette blue:")
    PrintPalette(paletteBlue)

def Main() -> None:
    CreatePalette()

if __name__ == "__main__":
    try:
        Main()
    except Exception as err:
        print("ERROR:")
        print(err)

