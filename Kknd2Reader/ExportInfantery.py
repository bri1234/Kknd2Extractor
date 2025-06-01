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

from typing import Any
import base64
import zlib

from Kknd2Reader.KkndFileContainer import ContainerFileType
from Kknd2Reader.KkndFileMobd import MobdFrame, MobdFile, MobdAnimation

def ExportFrame(frame : MobdFrame) -> dict[str, Any]:
    
    img = base64.b85encode(zlib.compress(frame.Image.Pixels)).decode("ASCII")
    colors = base64.b85encode(zlib.compress(frame.ColorPalette.GetColorsRgbBytearray())).decode("ASCII")

    return {
        "Width": frame.Image.Width,
        "Height": frame.Image.Height,
        "OffX": frame.OffsetX,
        "OffY": frame.OffsetY,
        "Points": [ { "Id": p.Id, "X": p.Px, "Y": p.Py } for p in frame.PointList],
        "Colors": colors,
        "Img": img
    }

def ExportAnimation(animation : MobdAnimation) -> list[Any]:

    return [ ExportFrame(frame) for frame in animation.FrameList ]

def ExportGraphics(fileList : ContainerFileType, deathFileIdx : int, deathAnimationIdx : int) -> dict[str, Any]:

    # TODO: it seems there are multiple death animations for some units

    deathMobd = MobdFile(fileList.FileList[deathFileIdx])
    deathAnimation = deathMobd.AnimationList[deathAnimationIdx]

    return {
        "Death": ExportAnimation(deathAnimation)
    }

def ExportUnit(fileList : ContainerFileType, id : int, name : str, price : int,
               deathFileIdx : int, deathAnimationIdx : int) -> dict[str, Any]:

    return {
        "Id": id,
        "Name": name,
        "Price": price,
        "Gfx": ExportGraphics(fileList, deathFileIdx, deathAnimationIdx)
    }

def ExportSurvivors(fileList : ContainerFileType) -> dict[str, Any]:

    return {
        "Army": "Survivors",
        "Units": [
            ExportUnit(fileList, 1, "Machine gunner", 100, 199, 3),
            ExportUnit(fileList, 2, "Grenadier", 125, 199, 2),
            ExportUnit(fileList, 3, "Flamer", 200, 199, 1),
            ExportUnit(fileList, 4, "Rocketeer", 200, 199, 7),
            ExportUnit(fileList, 5, "Kamikaze", 250, 4, 0),
            ExportUnit(fileList, 6, "Laser rifleman", 250, 199, 9),
            ExportUnit(fileList, 7, "Technician", 100, 199, 10)
        ]
    }

def ExportEvolved(fileList : ContainerFileType) -> dict[str, Any]:
    return {
        "Army": "Evolved",
        "Units": [
            ExportUnit(fileList, 1, "Berzerker", 100, 46, 3),
            ExportUnit(fileList, 2, "Rioter", 125, 46, 2),
            ExportUnit(fileList, 3, "Pyromaniac", 200, 46, 1),
            ExportUnit(fileList, 4, "Homing bazookoid", 200, 46, 4),
            ExportUnit(fileList, 5, "Martyr", 250, 4, 0),
            ExportUnit(fileList, 6, "Spirit archer", 250, 46, 5),
            ExportUnit(fileList, 7, "Mekanik", 100, 46, 6)
        ]
    }

def ExportSeries9(fileList : ContainerFileType) -> dict[str, Any]:
    return {
        "Army": "Series9",
        "Units": [
            ExportUnit(fileList, 1, "Seeder", 250, 125, 1),
            ExportUnit(fileList, 2, "Pod launcher", 300, 125, 2),
            ExportUnit(fileList, 3, "Weed killer", 450, 125, 4),
            ExportUnit(fileList, 4, "Spore missile", 450, 125, 3),
            ExportUnit(fileList, 5, "Michelangelo", 500, 4, 0),
            ExportUnit(fileList, 6, "Steriliser", 600, 125, 0),
            ExportUnit(fileList, 7, "Systech", 100, 125, 5)
        ]
    }
    
def ExportInfantery(fileList : ContainerFileType) -> dict[str, Any]:

    return {
        "Survivors": ExportSurvivors(fileList),
        "Evolved": ExportEvolved(fileList),
        "Series9": ExportSeries9(fileList)
    }

