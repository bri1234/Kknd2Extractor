
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

from Kknd2Reader.KkndFileMobd import MobdColorPalette
from termcolor import cprint
import colorsys
import os

def Rgb(rgb : int) -> tuple[int, int, int]:
    return (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, (rgb >> 0) & 0xFF

def GetHsv(rgb : int) -> tuple[float, float, float]:
    r = (rgb >> 16) & 0xFF
    g = (rgb >> 8) & 0xFF
    b = (rgb >> 0) & 0xFF

    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return h, s, v

def GetHsvStr(rgb : int) -> str:
    h, s, v = GetHsv(rgb)
    return f"({int(h * 255):02X} {int(s * 255):02X} {int(v * 255):02X})"

def ShowPalettes(fileName : str, paletteRed : list[int], paletteGre : list[int], paletteBlu : list[int]) -> None:
    with open(fileName, "w") as f:
        for idx in range(len(paletteRed)):
            red = paletteRed[idx]
            gre = paletteGre[idx]
            blu = paletteBlu[idx]
            diff = ""
            
            if red != gre or red != blu or gre != blu:
                diff = "D"

            f.write(f"{idx:03} {red:06X},{gre:06X},{blu:06X},   {diff}\n")

            print(f"{idx:03}", end="")
            cprint(f"\t{red:06X} {GetHsvStr(red)}", on_color=Rgb(red), end="")
            cprint(f"\t{gre:06X} {GetHsvStr(gre)}", on_color=Rgb(gre), end="")
            cprint(f"\t{blu:06X} {GetHsvStr(blu)}", on_color=Rgb(blu), end="")
            print(f"\t{diff}")

def Debug2(folder : str) -> None:
    print("START")

    colorList24 = MobdColorPalette.ColorsSeries9BuildingsRgbRed
    colorList15 : list[int] = []
    colorList15Bytes : list[bytes] = []
    colorList15Bytes2 : list[bytes] = []

    for color24 in colorList24:
        color15 = MobdColorPalette.ConvertRgb24To15(color24)

        if color24 == 0 or color15 == 0:
            continue

        colorList15.append(color15)
        colorList15Bytes.append(bytes([color15 & 0xFF, (color15 >> 8) & 0xFF]))

    for idx in range(0, len(colorList15Bytes) - 1, 2):
        colorBytes = colorList15Bytes[idx] + colorList15Bytes[idx + 1]
        colorList15Bytes2.append(colorBytes)

    founds : dict[str, int] = {}

    for fileName in os.listdir(folder):
        fullFileName = os.path.join(folder, fileName)
        if not os.path.isfile(fullFileName):
            continue
        
        print(f"test {fileName}")

        with open(fullFileName, "rb") as file:
            data = file.read()

        count = 0
        for colorBytes in colorList15Bytes2:
            count += data.count(colorBytes)

        print(count)
        founds[fullFileName] = count

    for item in founds:
        print(f"{item} = {founds[item]}")

if __name__ == "__main__":

    # ShowPalettes("colors series9.txt",
    #              MobdColorPalette.ColorsSeries9BuildingsRgbRed,
    #              MobdColorPalette.ColorsSeries9BuildingsRgbGre,
    #              MobdColorPalette.ColorsSeries9BuildingsRgbBlu)
    
    ShowPalettes("colors survivors.txt",
                 MobdColorPalette.ColorsSurvivorsBuildingsRgbRed,
                 MobdColorPalette.ColorsSurvivorsBuildingsRgbGre,
                 MobdColorPalette.ColorsSurvivorsBuildingsRgbBlu)
    
    # Debug2("/Daten1/kknd2/Kknd2MemoryDump")

