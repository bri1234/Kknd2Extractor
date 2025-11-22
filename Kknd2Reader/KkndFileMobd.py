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

import numpy as np
import numpy.typing as npt
from Kknd2Reader.DataBuffer import GetInt32LE, GetUInt32LE, GetUInt16LE, GetUInt8, GetStringReverse
from Kknd2Reader.KkndFileContainer import ContainerFile
from typing import Any
import colorsys

MobdFileStructure : dict[int, str] = {}

def SaveMobdFileStructureInfo(fileName : str) -> None:
    """ Exports the Mobd file structure of the last loaded file.

    Args:
        fileName (str): The filename.
    """
    with open(fileName, "w") as file:
        for offset in sorted(MobdFileStructure):
            file.write(f"{offset:06} {MobdFileStructure[offset]}\n")

def ConvertColorsFromRgbToBgr(colorsRgb : list[int]) -> list[int]:
    """ Converts RGB colors to BGR colors.

    Args:
        colorsRgb (list[int]): The RGB colors.

    Returns:
        list[int]: The BGR colors
    """
    
    colorsBgr = [0] * len(colorsRgb)

    for idx in range(len(colorsRgb)):
        c = colorsRgb[idx]
        colorsBgr[idx] = ((c & 0xFF) << 16) | (c & 0xFF00) | ((c & 0xFF0000) >> 16)

    return colorsBgr

class ModbPoint:
    """ This class represents one point.
    """

    Id : int = 0

    Px : int = 0
    Py : int = 0
    Pz : int = 0    # unused

    def ReadPoint(self, data : bytearray, position : int) -> int:
        """ Reads one point from the raw data.

        Args:
            data (bytearray): The raw data of the MOBD file.
            position (int): The position(=offset) of the point in the MOBD file.

        Returns:
            int: The position after this point.
        """

        self.Id = GetUInt32LE(data, position + 0)

        self.Px = GetInt32LE(data, position + 4) // 256
        self.Py = GetInt32LE(data, position + 8) // 256
        self.Pz = GetInt32LE(data, position + 12) // 256

        return position + 16

class MobdColorPalette:
    """ This class stores the color palette.
    """

    # all color palettes of the Mobd file
    MobdColorPalettes : dict[int, Any] = {}

    # 4 byte RGB color palette for Survivors buildings
    ColorsSurvivorsBuildingsRgbRed = [0x00000000,0x00000000,0x00181C10,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00211C08,0x00000000,0x00211C18,0x00291C10,0x00311C10,0x00000000,0x00292410,0x00292C10,0x00312408,0x00392C00,0x00312410,0x00312C10,0x00312C18,0x00392410,0x00392C10,0x00392C18,0x00313418,0x00393418,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00632C29,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00422410,0x00000000,0x00422C18,0x004A2C10,0x004A2C18,0x00423418,0x004A3410,0x00000000,0x00000000,0x00522C18,0x00000000,0x00000000,0x00523C18,0x005A3C18,0x00423421,0x00423C21,0x00423C29,0x004A3C21,0x004A3C29,0x00523421,0x005A3421,0x00000000,0x00633421,0x00000000,0x00000000,0x006B3C39,0x00733C29,0x00000000,0x00000000,0x00000000,0x004A4529,0x00524529,0x00524D29,0x005A4D29,0x00524D31,0x00525D21,0x005A5531,0x005A5539,0x00634518,0x00000000,0x00000000,0x006B5529,0x00635531,0x006B5D39,0x00734529,0x00734D21,0x00734D29,0x00735D31,0x007B5531,0x00636521,0x007B6D21,0x00736539,0x007B6539,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00635D42,0x00000000,0x00000000,0x007B6D4A,0x00000000,0x00000000,0x007B7D7B,0x00000000,0x00000000,0x00000000,0x00000000,0x00844D42,0x00000000,0x00000000,0x0094344A,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x008C3C73,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00C6556B,0x00000000,0x00000000,0x00000000,0x00DE656B,0x00000000,0x00000000,0x00000000,0x00000000,0x008C6539,0x00847539,0x009C5D5A,0x00847552,0x00847D52,0x00947D4A,0x008C865A,0x0094865A,0x00000000,0x009C8E63,0x00A58E63,0x00AD966B,0x00A59673,0x00AD9E73,0x00BD9E63,0x00B59E73,0x00B5A67B,0x00BDA673,0x00C6AE7B,0x00CEB67B,0x00D6BE7B,0x00000000,0x00000000,0x00000000,0x00948E84,0x00949694,0x009C9E9C,0x00AD6563,0x00000000,0x00000000,0x00A5AE9C,0x00ADA6A5,0x00B5B6B5,0x00BDBEBD,0x00000000,0x00000000,0x00C66D84,0x00000000,0x00000000,0x00000000,0x00CE75A5,0x00000000,0x00000000,0x00000000,0x00000000,0x00F7867B,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00CEB684,0x00D6BE84,0x00DEC784,0x00E7CF84,0x00E7CF8C,0x00F7D78C,0x00F7DF9C,0x00F7EF9C,0x00F7F7A5,0x00F7F7AD,0x00C6C7C6,0x00CECFCE,0x00D6D7D6,0x00DEDFDE,0x00000000,0x00000000,0x00F7CFCE,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00632C29,0x00844542,0x009C4D4A,0x00AD5552,0x00BD6563,0x00CE6D6B,0x00E77573,0x00FF7D7B,0x00FF8684,0x00FF8E8C,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000]
    ColorsSurvivorsBuildingsRgbGre = [0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00102C31,0x00000000,0x00211408,0x00000000,0x00000000,0x00211C18,0x00291C10,0x00000000,0x00000000,0x00292410,0x00292C10,0x00312408,0x00392C00,0x00312410,0x00312C10,0x00312C18,0x00392410,0x00392C10,0x00392C18,0x00313418,0x00393418,0x00000000,0x00000000,0x00000000,0x00000000,0x00393429,0x00000000,0x0010244A,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00317552,0x00000000,0x00000000,0x00000000,0x00000000,0x00422410,0x00000000,0x00422C18,0x004A2C10,0x004A2C18,0x00423418,0x004A3410,0x00000000,0x00000000,0x00522C18,0x00000000,0x00000000,0x00523C18,0x005A3C18,0x00423421,0x00423C21,0x00423C29,0x004A3C21,0x004A3C29,0x00523421,0x005A3421,0x00000000,0x00633421,0x00000000,0x00000000,0x006B3C39,0x00733C29,0x00000000,0x00000000,0x00000000,0x004A4529,0x00524529,0x00000000,0x005A4D29,0x00524D31,0x00525D21,0x005A5531,0x005A5539,0x00634518,0x00000000,0x00000000,0x006B5529,0x00635531,0x006B5D39,0x00734529,0x00734D21,0x00734D29,0x00735D31,0x007B5531,0x00636521,0x007B6D21,0x00736539,0x007B6539,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00427552,0x00000000,0x00000000,0x00000000,0x00635D42,0x00000000,0x00000000,0x007B6D4A,0x00000000,0x00000000,0x007B7D7B,0x00000000,0x00394584,0x00000000,0x00000000,0x005A7584,0x00000000,0x00000000,0x0042964A,0x00000000,0x00000000,0x00529E63,0x00000000,0x006B866B,0x00000000,0x00000000,0x007BB694,0x00000000,0x005A8E4A,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x0073AE73,0x006BC77B,0x007BCFA5,0x00000000,0x00000000,0x007BDF9C,0x00000000,0x00000000,0x00000000,0x00000000,0x008C6539,0x00847539,0x009C5D5A,0x00847552,0x00847D52,0x00947D4A,0x008C865A,0x0094865A,0x00000000,0x009C8E63,0x00A58E63,0x00AD966B,0x00A59673,0x00AD9E73,0x00BD9E63,0x00B59E73,0x00B5A67B,0x00BDA673,0x00C6AE7B,0x00CEB67B,0x00D6BE7B,0x00848694,0x00000000,0x00000000,0x00948E84,0x00000000,0x00000000,0x0084AE94,0x0084BE94,0x009CBEA5,0x00A5AE9C,0x00ADA6AD,0x00B5B6B5,0x00BDBEBD,0x00000000,0x00000000,0x008CC794,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x009CF7AD,0x00B5DFC6,0x00A5F7CE,0x00ADF7CE,0x009CEF94,0x00A5F79C,0x00000000,0x00000000,0x00000000,0x00000000,0x00CEB684,0x00D6BE84,0x00DEC784,0x00E7CF84,0x00E7CF8C,0x00F7D78C,0x00F7DF9C,0x00F7EF9C,0x00F7F7A5,0x00F7F7AD,0x00C6C7C6,0x00CECFCE,0x00D6D7D6,0x00DEDFDE,0x00000000,0x00000000,0x00F7CFCE,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00632C29,0x00844542,0x009C4D4A,0x00AD5552,0x00BD6563,0x00CE6D6B,0x00E77573,0x00FF7D7B,0x00FF8684,0x00FF8E8C,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000]
    ColorsSurvivorsBuildingsRgbBlu = [0x00000000,0x00100C08,0x00181C10,0x00101421,0x00101C21,0x00101C31,0x00102421,0x00102C31,0x00182439,0x00211408,0x00211C08,0x00291C08,0x00211C18,0x00291C10,0x00311C10,0x00212410,0x00292410,0x00292C10,0x00312408,0x00392C00,0x00312410,0x00312C10,0x00312C18,0x00392410,0x00392C10,0x00392C18,0x00313418,0x00393418,0x00292421,0x00292C29,0x00212C39,0x00293439,0x00393429,0x00393C39,0x0010244A,0x00213442,0x00293C4A,0x0029345A,0x00393C52,0x00000000,0x00313C73,0x00314563,0x0039456B,0x00314D73,0x0039556B,0x00422410,0x00422C10,0x00422C18,0x004A2C10,0x004A2C18,0x00423418,0x004A3410,0x004A3418,0x00000000,0x00522C18,0x00523410,0x00523418,0x00523C18,0x005A3C18,0x00423421,0x00423C21,0x00423C29,0x004A3C21,0x004A3C29,0x00523421,0x005A3421,0x00633C18,0x00633421,0x00633C21,0x006B3C21,0x006B3C39,0x00733C29,0x00424510,0x004A5518,0x004A4521,0x004A4529,0x00524529,0x00524D29,0x005A4D29,0x00524D31,0x00525D21,0x005A5531,0x005A5539,0x00634518,0x006B4518,0x00734D18,0x006B5529,0x00635531,0x006B5D39,0x00734529,0x00734D21,0x00734D29,0x00735D31,0x007B5531,0x00636521,0x007B6D21,0x00736539,0x007B6539,0x00000000,0x00424542,0x00424D52,0x004A555A,0x00524D4A,0x005A5552,0x00424D63,0x00424D73,0x00425D73,0x0052556B,0x005A5D73,0x00635D42,0x00635D63,0x00736542,0x007B6D4A,0x006B6D6B,0x00737573,0x007B7D7B,0x0031458C,0x00394584,0x00425584,0x004A5D8C,0x005A5D84,0x004A6584,0x004A6D8C,0x00426594,0x0052658C,0x005A6D84,0x00526D9C,0x005A75A5,0x006B7584,0x00637594,0x00737D84,0x006B75A5,0x005A7DC6,0x004A868C,0x005A86A5,0x00738694,0x006B86A5,0x006386B5,0x007B86B5,0x007396AD,0x00000000,0x007B86CE,0x007B8EC6,0x007396CE,0x007B96DE,0x00000000,0x007BA6C6,0x00842C21,0x00846D39,0x008C6539,0x00847539,0x009C5D5A,0x00847552,0x00847D52,0x00947D4A,0x008C865A,0x0094865A,0x0084867B,0x009C8E63,0x00A58E63,0x00AD966B,0x00A59673,0x00AD9E73,0x00BD9E63,0x00B59E73,0x00B5A67B,0x00BDA673,0x00C6AE7B,0x00CEB67B,0x00D6BE7B,0x00848694,0x00848E9C,0x008C9E9C,0x00948E84,0x00949694,0x009C9E9C,0x00848EAD,0x008496BD,0x009CA6BD,0x00A5AE9C,0x00ADA6A5,0x00B5B6B5,0x00BDBEBD,0x00849EDE,0x00000000,0x008CA6C6,0x008CAEDE,0x00000000,0x008CBEDE,0x009CBECE,0x0084A6F7,0x008CB6F7,0x009CBEF7,0x00B5BEDE,0x00A5AEF7,0x00ADB6F7,0x0094CFEF,0x009CD7F7,0x00B5C7F7,0x00B5DFF7,0x00000000,0x00BDEFF7,0x00CEB684,0x00D6BE84,0x00DEC784,0x00E7CF84,0x00E7CF8C,0x00F7D78C,0x00F7DF9C,0x00F7EF9C,0x00F7F7A5,0x00F7F7AD,0x00C6C7C6,0x00CECFCE,0x00D6D7D6,0x00DEDFDE,0x00DEE7F7,0x00D6F7F7,0x00F7CFCE,0x00000000,0x00E7E7E7,0x00F7F7EF,0x00000000,0x00000000,0x00000000,0x00FFFFFF,0x00000000,0x00000000,0x00000000,0x00000000,0x00632C29,0x00844542,0x009C4D4A,0x00AD5552,0x00BD6563,0x00CE6D6B,0x00E77573,0x00FF7D7B,0x00FF8684,0x00FF8E8C,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000]

    # 4 byte RGB color palette for Series 9 buildings
    ColorsSeries9BuildingsRgbRed=[0x00000000,0x00000400,0x00080C08,0x00080C08,0x00101410,0x00101410,0x00181C18,0x00181C18,0x00212421,0x00212421,0x00292C29,0x00292421,0x00292C29,0x00313431,0x00312C29,0x00313431,0x00393C39,0x00393431,0x00393C39,0x00424542,0x00424542,0x00424542,0x004A4D4A,0x004A4D4A,0x00525552,0x00524D4A,0x00525552,0x00525552,0x005A5D5A,0x005A5D5A,0x00636563,0x00635D5A,0x00636563,0x00636563,0x006B6D6B,0x006B6563,0x006B6D6B,0x006B6D6B,0x00737573,0x00737573,0x007B7D7B,0x007B7D7B,0x007B7D7B,0x00848684,0x00847D7B,0x00848684,0x008C8E8C,0x008C8E8C,0x008C8E8C,0x00949694,0x00949694,0x009C9E9C,0x009C9E9C,0x00A5A6A5,0x00A5A6A5,0x00ADAEAD,0x00AD9694,0x00ADAEAD,0x00ADAEAD,0x00B5B6B5,0x00B5AEAD,0x00B5B6B5,0x00BDBEBD,0x00BDBEBD,0x00C6C7C6,0x00C6C7C6,0x00CECFCE,0x00CECFCE,0x00D6D7D6,0x00D6D7D6,0x00DEDFDE,0x00DEDFDE,0x00E7E7E7,0x00E7E7E7,0x00EFEFEF,0x00F7F7F7,0x00FFFFFF,0x008C867B,0x00393429,0x0084756B,0x006B655A,0x0073655A,0x00080400,0x00423C31,0x00524D42,0x005A5542,0x00635542,0x007B756B,0x00A59684,0x00522421,0x005A2421,0x006B2421,0x00632C31,0x00732C29,0x007B2C31,0x007B3C39,0x008C3439,0x008C3C39,0x008C3439,0x00943431,0x009C3C42,0x008C3C42,0x009C3C42,0x00AD3C42,0x00AD3C39,0x00B53C42,0x00B54542,0x00BD4552,0x00C64D52,0x00C6454A,0x00AD454A,0x00B54D52,0x00C64D52,0x00BD5D6B,0x00C64D52,0x00C6555A,0x00CE4D52,0x00CE4D5A,0x00D65563,0x00D65D63,0x00DE4D5A,0x00DE555A,0x00DE4D52,0x00F75563,0x00EF5D6B,0x00F75D6B,0x00FF5563,0x00FF5D6B,0x00FF5D5A,0x00FF5D63,0x00FF756B,0x00FF7D73,0x00FF7584,0x00FF7D7B,0x00FF9694,0x00FF9E9C,0x00292C29,0x00393C39,0x00424539,0x004A4D42,0x00848684,0x00101C18,0x00293431,0x00313431,0x00424542,0x00424D4A,0x004A5552,0x006B7573,0x00737D7B,0x007B8684,0x007B8684,0x007B8684,0x00A5AEAD,0x00A5AEAD,0x00ADB6B5,0x00CEDFDE,0x00DEE7E7,0x0042E7F7,0x0042EFF7,0x004AF7FF,0x0039C7D6,0x0039CFDE,0x005ADFE7,0x00738684,0x00848E94,0x008C969C,0x0094A6A5,0x00A5AEB5,0x00ADB6BD,0x007B8684,0x006B7573,0x006B757B,0x00848E94,0x0094A6AD,0x0052555A,0x00000418,0x00181C21,0x00212429,0x00292C29,0x00212429,0x00313431,0x00313439,0x00393C39,0x00393C42,0x0042454A,0x004A4D52,0x00525552,0x0052555A,0x005A5D63,0x00636563,0x0063656B,0x006B6D6B,0x00737573,0x00848684,0x006B6D84,0x0084868C,0x008C8E8C,0x0073758C,0x00949694,0x0094969C,0x009C9E9C,0x00A5A6AD,0x00ADAEAD,0x00ADAEB5,0x00393C52,0x00312C4A,0x00211C31,0x009486B5,0x00AD96C6,0x00392C4A,0x005A556B,0x00634D84,0x0052455A,0x0063656B,0x007B757B,0x00181C18,0x00393439,0x00424542,0x004A454A,0x004A4D4A,0x005A555A,0x00736D73,0x00737573,0x00FFFFFF,0x00523421,0x00734D29,0x007B5531,0x006B4518,0x00734D21,0x00634518,0x004A3C21,0x00312C18,0x00635531,0x006B5D39,0x004A4529,0x00524D29,0x005A5531,0x00636521,0x004A5518,0x00000000,0x00311400,0x00522C08,0x005A3410,0x004A2400,0x00000000,0x00422400,0x00291C00,0x00100C00,0x00423410,0x004A3C18,0x00292408,0x00312C08,0x00393410,0x00424500,0x00293400,0x00000400]
    ColorsSeries9BuildingsRgbGre=[0x00000000,0x00000400,0x00080C08,0x00080C08,0x00101410,0x00101410,0x00181C18,0x00181C18,0x00212421,0x00212421,0x00292C29,0x00292421,0x00292C29,0x00313431,0x00312C29,0x00313431,0x00393C39,0x00393431,0x00393C39,0x00424542,0x00424542,0x00424542,0x004A4D4A,0x004A4D4A,0x00525552,0x00524D4A,0x00525552,0x00525552,0x005A5D5A,0x005A5D5A,0x00636563,0x00635D5A,0x00636563,0x00636563,0x006B6D6B,0x006B6563,0x006B6D6B,0x006B6D6B,0x00737573,0x00737573,0x007B7D7B,0x007B7D7B,0x007B7D7B,0x00848684,0x00847D7B,0x00848684,0x008C8E8C,0x008C8E8C,0x008C8E8C,0x00949694,0x00949694,0x009C9E9C,0x009C9E9C,0x00A5A6A5,0x00A5A6A5,0x00ADAEAD,0x00AD9694,0x00ADAEAD,0x00ADAEAD,0x00B5B6B5,0x00B5AEAD,0x00B5B6B5,0x00BDBEBD,0x00BDBEBD,0x00C6C7C6,0x00C6C7C6,0x00CECFCE,0x00CECFCE,0x00D6D7D6,0x00D6D7D6,0x00DEDFDE,0x00DEDFDE,0x00E7E7E7,0x00E7E7E7,0x00EFEFEF,0x00F7F7F7,0x00FFFFFF,0x008C867B,0x00393429,0x0084756B,0x006B655A,0x0073655A,0x00080400,0x00423C31,0x00524D42,0x005A5542,0x00635542,0x007B756B,0x00A59684,0x00001400,0x00082408,0x00082C08,0x00102410,0x00103410,0x00183C18,0x00213C21,0x00214D21,0x00214D21,0x00214D21,0x00214D21,0x00295529,0x00294D29,0x00295D29,0x00316531,0x00296531,0x00316D31,0x00316D31,0x00397539,0x00397539,0x00397D39,0x00396539,0x00396D39,0x00427542,0x0052754A,0x00427D42,0x004A7D4A,0x00428642,0x00428642,0x00528E52,0x00528E52,0x004A8E4A,0x004A8E4A,0x004A964A,0x0052A652,0x005A9E5A,0x005AA65A,0x0052AE5A,0x0063B663,0x005AB663,0x0063B663,0x006BB67B,0x0073B67B,0x007BB67B,0x007BB684,0x0094B69C,0x009CB69C,0x00292C29,0x00393C39,0x00424539,0x004A4D42,0x00848684,0x00101C18,0x00293431,0x00313431,0x00424542,0x00424D4A,0x004A5552,0x006B7573,0x00737D7B,0x007B8684,0x007B8684,0x007B8684,0x00A5AEAD,0x00A5AEAD,0x00ADB6B5,0x00CEDFDE,0x00DEE7E7,0x0042E7F7,0x0042EFF7,0x004AF7FF,0x0039C7D6,0x0039CFDE,0x005ADFE7,0x00738684,0x00848E94,0x008C969C,0x0094A6A5,0x00A5AEB5,0x00ADB6BD,0x007B8684,0x006B7573,0x006B757B,0x00848E94,0x0094A6AD,0x0052555A,0x00000418,0x00181C21,0x00212429,0x00292C29,0x00212429,0x00313431,0x00313439,0x00393C39,0x00393C42,0x0042454A,0x004A4D52,0x00525552,0x0052555A,0x005A5D63,0x00636563,0x0063656B,0x006B6D6B,0x00737573,0x00848684,0x006B6D84,0x0084868C,0x008C8E8C,0x0073758C,0x00949694,0x0094969C,0x009C9E9C,0x00A5A6AD,0x00ADAEAD,0x00ADAEB5,0x00393C52,0x00312C4A,0x00211C31,0x009486B5,0x00AD96C6,0x00392C4A,0x005A556B,0x00634D84,0x0052455A,0x0063656B,0x007B757B,0x00181C18,0x00393439,0x00424542,0x004A454A,0x004A4D4A,0x005A555A,0x00736D73,0x00737573,0x00FFFFFF,0x00523421,0x00734D29,0x007B5531,0x006B4518,0x00734D21,0x00634518,0x004A3C21,0x00312C18,0x00635531,0x006B5D39,0x004A4529,0x00524D29,0x005A5531,0x00636521,0x004A5518,0x00000000,0x00311400,0x00522C08,0x005A3410,0x004A2400,0x00000000,0x00422400,0x00291C00,0x00100C00,0x00423410,0x004A3C18,0x00292408,0x00312C08,0x00393410,0x00424500,0x00293400,0x00000400]
    ColorsSeries9BuildingsRgbBlu=[0x00000000,0x00000400,0x00080C08,0x00080C08,0x00101410,0x00101410,0x00181C18,0x00181C18,0x00212421,0x00212421,0x00292C29,0x00292421,0x00292C29,0x00313431,0x00312C29,0x00313431,0x00393C39,0x00393431,0x00393C39,0x00424542,0x00424542,0x00424542,0x004A4D4A,0x004A4D4A,0x00525552,0x00524D4A,0x00525552,0x00525552,0x005A5D5A,0x005A5D5A,0x00636563,0x00635D5A,0x00636563,0x00636563,0x006B6D6B,0x006B6563,0x006B6D6B,0x006B6D6B,0x00737573,0x00737573,0x007B7D7B,0x007B7D7B,0x007B7D7B,0x00848684,0x00847D7B,0x00848684,0x008C8E8C,0x008C8E8C,0x008C8E8C,0x00949694,0x00949694,0x009C9E9C,0x009C9E9C,0x00A5A6A5,0x00A5A6A5,0x00ADAEAD,0x00AD9694,0x00ADAEAD,0x00ADAEAD,0x00B5B6B5,0x00B5AEAD,0x00B5B6B5,0x00BDBEBD,0x00BDBEBD,0x00C6C7C6,0x00C6C7C6,0x00CECFCE,0x00CECFCE,0x00D6D7D6,0x00D6D7D6,0x00DEDFDE,0x00DEDFDE,0x00E7E7E7,0x00E7E7E7,0x00EFEFEF,0x00F7F7F7,0x00FFFFFF,0x008C867B,0x00393429,0x0084756B,0x006B655A,0x0073655A,0x00080400,0x00423C31,0x00524D42,0x005A5542,0x00635542,0x007B756B,0x00A59684,0x00181C31,0x00212439,0x00212C4A,0x00292C42,0x00293452,0x00313C5A,0x0039455A,0x0039456B,0x00424D6B,0x0039456B,0x00394573,0x00424D7B,0x00424D6B,0x004A557B,0x004A5584,0x004A558C,0x00525D94,0x00525D94,0x005A6594,0x005A659C,0x005A65A5,0x00526584,0x005A6D94,0x005A6D9C,0x006B7D94,0x00636DA5,0x006B75A5,0x005A6DAD,0x006375AD,0x00737DAD,0x007386AD,0x006B7DB5,0x006B7DB5,0x006B75BD,0x007386CE,0x007B8EC6,0x007B8ECE,0x00738ED6,0x008496E7,0x007B8EE7,0x008496E7,0x009496E7,0x009496E7,0x00A5AEE7,0x00A5A6E7,0x00BDBEE7,0x00CECFE7,0x00292C29,0x00393C39,0x00424539,0x004A4D42,0x00848684,0x00101C18,0x00293431,0x00313431,0x00424542,0x00424D4A,0x004A5552,0x006B7573,0x00737D7B,0x007B8684,0x007B8684,0x007B8684,0x00A5AEAD,0x00A5AEAD,0x00ADB6B5,0x00CEDFDE,0x00DEE7E7,0x0042E7F7,0x0042EFF7,0x004AF7FF,0x0039C7D6,0x0039CFDE,0x005ADFE7,0x00738684,0x00848E94,0x008C969C,0x0094A6A5,0x00A5AEB5,0x00ADB6BD,0x007B8684,0x006B7573,0x006B757B,0x00848E94,0x0094A6AD,0x0052555A,0x00000418,0x00181C21,0x00212429,0x00292C29,0x00212429,0x00313431,0x00313439,0x00393C39,0x00393C42,0x0042454A,0x004A4D52,0x00525552,0x0052555A,0x005A5D63,0x00636563,0x0063656B,0x006B6D6B,0x00737573,0x00848684,0x006B6D84,0x0084868C,0x008C8E8C,0x0073758C,0x00949694,0x0094969C,0x009C9E9C,0x00A5A6AD,0x00ADAEAD,0x00ADAEB5,0x00393C52,0x00312C4A,0x00211C31,0x009486B5,0x00AD96C6,0x00392C4A,0x005A556B,0x00634D84,0x0052455A,0x0063656B,0x007B757B,0x00181C18,0x00393439,0x00424542,0x004A454A,0x004A4D4A,0x005A555A,0x00736D73,0x00737573,0x00FFFFFF,0x00523421,0x00734D29,0x007B5531,0x006B4518,0x00734D21,0x00634518,0x004A3C21,0x00312C18,0x00635531,0x006B5D39,0x004A4529,0x00524D29,0x005A5531,0x00636521,0x004A5518,0x00000000,0x00311400,0x00522C08,0x005A3410,0x004A2400,0x00000000,0x00422400,0x00291C00,0x00100C00,0x00423410,0x004A3C18,0x00292408,0x00312C08,0x00393410,0x00424500,0x00293400,0x00000400]

    # 4 byte RGB color palette for Evolved buildings
    ColorsEvolvedBuildingsRgb=[0x0000FB00,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x0000FFFF,0x0000F6F6,0x0000EEEE,0x0000E6E6,0x0000DEDE,0x0000D5D5,0x0000CDCD,0x0000C5C5,0x00FBE3F3,0x00EBAAEB,0x00E392E3,0x00613161,0x00CA79D2,0x00AA59B2,0x008A419A,0x0020E3FB,0x008AF3FB,0x0000FBFB,0x00B2FBFB,0x00518259,0x00E3FBE3,0x008AC28A,0x00395128,0x00C2FB49,0x00FBFB41,0x00FBFBCA,0x00FBFBDB,0x00595900,0x00393931,0x00FBF3A2,0x00B2A200,0x00FBE328,0x00FBE359,0x00FBEBAA,0x00F3EBCA,0x00F3DB8A,0x00FBC220,0x00F3CA59,0x00F3B208,0x00715100,0x00FBDB92,0x00F3DBA2,0x00BA8208,0x00AA7100,0x00312818,0x00CA8A20,0x00927139,0x008A7149,0x00594118,0x00FBA220,0x00F3C279,0x00D29A49,0x00BA9A69,0x00AA8A59,0x008A5910,0x00715120,0x00695941,0x00594931,0x00FBCA8A,0x00D2AA71,0x00796141,0x00FBAA49,0x00EB9220,0x009A7951,0x00E37900,0x00BA6100,0x00B27128,0x008A6131,0x00824908,0x00EB7908,0x00BAA28A,0x009A8A79,0x00695139,0x00613910,0x00614120,0x00513920,0x00514131,0x00493928,0x00413120,0x00201810,0x00F38A28,0x00C28249,0x00392008,0x00FBBA9A,0x00201008,0x00392820,0x00925139,0x00824128,0x00FBA28A,0x008A4939,0x00715149,0x00280800,0x00B26151,0x00A25949,0x00693931,0x00512820,0x00411810,0x00EB7169,0x00FBFBFB,0x00DBDBDB,0x00D50000,0x00C2C2C2,0x00B0B0B0,0x009F9F9F,0x008E8E8E,0x007C7C7C,0x006B6B6B,0x005A5A5A,0x00494949,0x00494949,0x00202020,0x00000000,0x00FB6161,0x00FB2020,0x00FB0000,0x00DBD4FB,0x00E5A1A1,0x00FB7171,0x00FF5151,0x00ED1515,0x00CF0F0F,0x00B20B0B,0x00950707,0x00780404,0x005B0202,0x003E0000,0x00000000]

    # 4 byte RGB color read from MOBD file
    # this color palette is not valid for buildings
    ColorsRgb : list[int]

    # 4 byte BGR color read from MOBD file
    # this color palette is not valid for buildings
    ColorsBgr : list[int]

    # the animation index in the animation list
    AnimationIndex : int

    # the frame index in the animation
    FrameIndex : int

    # the palette position in the Mobd file
    PalettePosition : int

    def __init__(self, animationIndex : int, frameIndex : int) -> None:
        self.ColorsRgb = []
        self.ColorsBgr = []
        self.AnimationIndex = animationIndex
        self.FrameIndex = frameIndex

    def GetColorsRgbBytearray(self) -> bytearray:
        """ Converts the colors into a byte array.

        Returns:
            bytearray: The colors as little endian byte array.
        """
        b = bytearray()

        for color in self.ColorsRgb:
            b.extend(color.to_bytes(4, "little"))

        return b
    
    def ReadPalette(self, data : bytearray, palettePosition : int) -> None:
        """ Reads the color palette from the KKN2 data and stores it internally as a list of RGB values.

        Args:
            data (bytearray): The raw KKND2 data.
            palettePosition (int): The position of the color palette in the data buffer.
        """

        MobdFileStructure[palettePosition] = f"MobdColorPalette animation {self.AnimationIndex:03} frame {self.FrameIndex:03}"
        MobdColorPalette.MobdColorPalettes[palettePosition] = self
        self.PalettePosition = palettePosition

        self.ColorsRgb = []
        self.ColorsBgr = []
        numberOfColors = GetUInt16LE(data, palettePosition + 12)
        # print(f"# colors: {numberOfColors}")

        colorPosition = palettePosition + 14

        for _ in range(numberOfColors):
            color16 = GetUInt16LE(data, colorPosition)
            colorPosition += 2

            self.ColorsRgb.append(MobdColorPalette.ConvertRgb15To24(color16))

        self.__CreateBgrPalette()

    def __CreateBgrPalette(self) -> None:
        """ Creates the BGR palette from the RGB palette.
        """
        self.ColorsBgr = []

        for rgb in self.ColorsRgb:
            red   = (rgb >> 16) & 0xFF
            green = (rgb >>  8) & 0xFF
            blue  = (rgb >>  0) & 0xFF
            self.ColorsBgr.append((blue << 16) | (green << 8) | red)

    @staticmethod
    def CreateColorGradient(baseColorRgb : int, numberOfColors : int, valueStart : float = 0.15, valueEnd : float = 1.0) -> list[int]:
        colorList : list[int] = []

        r = ((baseColorRgb >> 16) & 0xFF) / 255.0
        g = ((baseColorRgb >>  8) & 0xFF) / 255.0
        b = ((baseColorRgb >>  0) & 0xFF) / 255.0

        h, s, _ = colorsys.rgb_to_hsv(r, g, b)

        for idx in range(numberOfColors):
            v = valueStart + idx / (numberOfColors - 1) * (valueEnd - valueStart)

            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            rgb = (int(r * 255.0) << 16) | (int(g * 255.0) << 8) | (int(b * 255.0) << 0)

            colorList.append(rgb)
            
        return colorList

    def ColorizeSeries9Building(self, baseColorRgb : int) -> list[int]:
        colorList = MobdColorPalette.CreateColorGradient(baseColorRgb, 47)

        colorsRgb = MobdColorPalette.ColorsSeries9BuildingsRgbRed.copy()
        for idx in range(len(colorList)):
            colorsRgb[89 + idx] = colorList[idx]

        return colorsRgb
    
    @staticmethod
    def ConvertRgb15To24(color16 : int) -> int:
        red   = ((color16 & 0x7C00) >> 7) & 0xFF
        green = ((color16 & 0x03E0) >> 2) & 0xFF
        blue  = ((color16 & 0x001F) << 3) & 0xFF

        return (red << 16) | (green << 8) | blue
    
    @staticmethod
    def ConvertRgb24To15(color24 : int) -> int:
        red   = (color24 >> 16) & 0xFF
        green = (color24 >>  8) & 0xFF
        blue  = (color24 >>  0) & 0xFF

        return ((red << 7) & 0x7C00) | ((green << 2) & 0x03E0) | ((blue >> 3) & 0x001F)

class MobdImage:
    """ This class stores the pixel data of an image.
        The image uses an indexed color palette.
    """

    # The image width in pixels.
    Width : int = 0

    # The image height in pixels.
    Height : int = 0

    # The image pixel data. A Pixel is an index in the color palette.
    Pixels : bytearray

    Has256Colors : bool

    # the animation index in the animation list
    AnimationIndex : int

    # the frame index in the animation
    FrameIndex : int

    def __init__(self, animationIndex : int, frameIndex : int) -> None:
        self.Pixels = bytearray()
        self.AnimationIndex = animationIndex
        self.FrameIndex = frameIndex

    def GetPixel(self, column : int, row : int) -> int:
        """ Returns one pixel.

        Args:
            x (int): Pixel column in the image.
            y (int): Pixel row in the image.

        Returns:
            int: The pixel = Index in the color palette.
        """
        return self.Pixels[column + row * self.Width]
    
    def ReadImage(self, data : bytearray, imagePosition : int, flags : int) -> None:
        """ Read the image from the raw data.

        Args:
            data (bytearray): The raw data.
            imagePosition (int): The image position in the data buffer.
            flags (int): Image flags read from the raw data.
        """
        MobdFileStructure[imagePosition] = f"MobdImage animation {self.AnimationIndex:03} frame {self.FrameIndex:03}"

        self.Pixels = bytearray()

        self.Width = GetInt32LE(data, imagePosition + 0)
        self.Height = GetInt32LE(data, imagePosition + 4)

        isFlipped = (flags & (1 << 31)) != 0
        isCompressed = (flags & (1 << 27)) != 0
        self.Has256Colors = (flags & (1 << 26)) != 0

        pixelDataPosition = imagePosition + 8

        if isCompressed:
            self.Pixels = MobdImage.__DecompressImageData(data, pixelDataPosition, self.Width, self.Height, self.Has256Colors)
        else:
            self.Pixels = data[pixelDataPosition : pixelDataPosition + self.Width * self.Height]

        if isFlipped:
            self.Pixels = MobdImage.__FlipImagePixels(self.Pixels, self.Width, self.Height)

    @staticmethod
    def __DecompressImageData(data : bytearray, pixelDataPosition : int, width : int, height : int, has256Colors : bool) -> bytearray:
        """ Decompress the image data.

        Args:
            data (bytearray): The raw image data.
            pixelDataPosition (int): The position of the raw image data in the data buffer.
            width (int): The image width in pixels.
            height (int): _The image height in pixels.
            has256Colors (bool): True if the image has 256 colors.

        Returns:
            bytearray: The decompressed image data.
        """

        size = width * height
        pixels = bytearray()
        position = pixelDataPosition

        while len(pixels) < size:

            if has256Colors:
                compressedSize = GetUInt16LE(data, position)
                position += 2
            else:
                compressedSize = GetUInt8(data, position)
                position += 1

            if compressedSize == 0:
                # store empty row
                pixels.extend([0] * width)

            elif (not has256Colors) and (compressedSize > 0x80):
                pixelCount = compressedSize - 0x80
                cnt = 0

                for _ in range(pixelCount):
                    twoPixels = GetUInt8(data, position)
                    position += 1

                    # store first pixel
                    pixels.append((twoPixels & 0xF0) >> 4)
                    cnt += 1

                    # store second pixel
                    if cnt < width:
                        pixels.append(twoPixels & 0x0F)
                        cnt += 1
                
            else:
                lineEndOffset = position + compressedSize
                while position < lineEndOffset:
                    chunkSize = GetUInt8(data, position)
                    position += 1

                    if chunkSize < 0x80:
                        pixels.extend([0] * chunkSize)
                    else:
                        pixelCount = chunkSize - 0x80

                        if has256Colors:
                            pixels.extend(data[position : position + pixelCount])
                            position += pixelCount

                        else:
                            numBytes = pixelCount // 2 + pixelCount % 2

                            for idx in range(numBytes):
                                twoPixels = GetUInt8(data, position)
                                position += 1

                                pixels.append((twoPixels & 0xF0) >> 4)

                                if (idx + 1 < numBytes) or (pixelCount % 2 == 0):
                                    pixels.append(twoPixels & 0x0F)

            cnt = (width - len(pixels) % width) % width
            if cnt > 0:
                pixels.extend([0] * cnt)
        
        return pixels
    
    @staticmethod
    def __FlipImagePixels(pixels : bytearray, width : int, height : int) -> bytearray:
        """ Flips the image pixels left <-> right.

        Args:
            pixels (bytearray): The pixel array.
            width (int): The image width in pixels.
            height (int): The image height in pixels.

        Returns:
            bytearray: The flipped pixel data.
        """

        flippedPixels = bytearray()

        for rowIdx in range(height):
            row = pixels[rowIdx * width : (rowIdx + 1) * width]
            row.reverse()

            flippedPixels.extend(row)

        return flippedPixels

class MobdFrame:
    """ This is one frame of the animation. This is an image with its color palette.
    """

    # The sprite offset from the center point of the image:
    # SpriteOffsetX = width / 2 - x
    # SpriteOffsetY = height / 2 - y
    OffsetX : int = 0
    OffsetY : int = 0

    # Points are required for turrets, muzzles and projectile launch offsets.
    PointList : list[ModbPoint]

    # The image colors.
    ColorPalette : MobdColorPalette

    # The image pixel data.
    Image : MobdImage

    Bitmap : Any

    # the raw file data
    RawFrameData : bytes

    # the animation index in the animation list
    AnimationIndex : int

    # the frame index in the animation
    FrameIndex : int

    def __init__(self, animationIndex : int, frameIndex : int) -> None:
        self.PointList = []
        self.Bitmap = None
        self.ColorPalette = MobdColorPalette(animationIndex, frameIndex)
        self.Image = MobdImage(animationIndex, frameIndex)
        self.AnimationIndex = animationIndex
        self.FrameIndex = frameIndex
    
    def ReadFrame(self, data : bytearray, framePosition : int, fileOffset : int) -> None:
        """ Reads one frame from the animation.

        Args:
            data (bytearray): The raw data of the MOBD file.
            framePosition (int): The position(=offset) of the frame in the MOBD file.
        """
        MobdFileStructure[framePosition] = f"MobdFrame animation {self.AnimationIndex:03} frame {self.FrameIndex:03}"

        self.OffsetX = GetInt32LE(data, framePosition + 0)
        self.OffsetY = GetInt32LE(data, framePosition + 4)

        renderFlagsOffset = GetUInt32LE(data, framePosition + 12)
        boxListOffset = GetUInt32LE(data, framePosition + 16)      # 2 points, min and max (???)
        pointListOffset = GetUInt32LE(data, framePosition + 24)

        # Comment from OpenKrush:
        # // Theoretically we could also read the boxes here.
		# // However they contain info about hitshapes etc. We define them in yaml to be able to tweak them.
		# // But the points are required for turrets, muzzles and projectile launch offsets.

        if pointListOffset > 0:
            self.PointList = self.__ReadPointList(data, pointListOffset - fileOffset)

        if renderFlagsOffset > 0:
            self.Image, self.ColorPalette = self.__ReadImageAndColorPalette(data, renderFlagsOffset - fileOffset, fileOffset)

        if boxListOffset > 0:
            self.__ReadBoxList(data, boxListOffset - fileOffset)

    def RenderFrameUInt32Abgr(self) -> npt.NDArray[np.uint32]:
        """ Renders the tile as ABGR data.
        """

        img = self.Image
        colorsBgr = self.ColorPalette.ColorsBgr
        pixels = np.zeros((img.Width, img.Height), np.uint32)
        unknownPixels : dict[int, int] = {}

        numColorsIs16 = len(colorsBgr) == 16

        if numColorsIs16:
            # colorsRgb = self.ColorPalette.ColorizeSeries9Building(0x19a3e1)
            # colorsBgr = ConvertColorsFromRgbToBgr(colorsRgb)
            # colorsBgr = ConvertColorsFromRgbToBgr(MobdColorPalette.ColorsSeries9BuildingsRgbRed)
            colorsBgr = ConvertColorsFromRgbToBgr(MobdColorPalette.ColorsSurvivorsBuildingsRgbBlu)

        # print(f"# colors: {len(colorsBgr)}")

        for row in range(img.Height):
            for column in range(img.Width):
                pixelValue = img.GetPixel(column, row)

                if pixelValue >= len(colorsBgr):
                    # raise Exception(f"Can not render imager, invalid pixel value: {pixel}")
                    pixelAbgrColor = 0xFF00FF00 | (pixelValue & 0xFF)
                    # pixelAbgrColor = 0xFFD000FF
                    unknownPixels[pixelValue] = unknownPixels[pixelValue] + 1 if pixelValue in unknownPixels else 1

                else:
                    # pixel is transparent if pixel value is 0
                    pixelAbgrColor = (colorsBgr[pixelValue] | 0xFF000000) if pixelValue != 0 else 0x00000000

                    if numColorsIs16 and pixelValue != 0 and colorsBgr[pixelValue] == 0:
                        print(f"### animation {self.AnimationIndex} frame {self.FrameIndex} pixel is undef: val={pixelValue} col={column} row={row}")

                pixels[column, row] = pixelAbgrColor
        
        if len(unknownPixels) > 0:
            print("Unknown pixels:")
            for pixelValue in unknownPixels.keys():
                print(f"pixel {pixelValue}: count {unknownPixels[pixelValue]}")
            pass

        return pixels

    def __ReadImageAndColorPalette(self, data : bytearray, position : int, fileOffset : int) -> tuple[MobdImage, MobdColorPalette]:
        """ Reads the image and the color palette from the raw data.

        Args:
            data (bytearray): The raw data buffer.
            position (int): The position of the image and color palette in the raw data buffer.
            fileOffset (int): The offset of the image file in the file container.

        Returns:
            tuple[MobdImage, MobdPalette]: The image and the color palette.
        """
        MobdFileStructure[position] = f"MobdFrame animation {self.AnimationIndex:03} frame {self.FrameIndex:03}"

        frameType = GetStringReverse(data, position + 0, 4)
        if frameType != "SPRC" and frameType != "SPNS":
            raise Exception(f"Invalid frame format: {frameType}")
        
        flags = GetUInt32LE(data, position + 4)
        paletteOffset = GetUInt32LE(data, position + 8)
        imageOffset = GetUInt32LE(data, position + 12)

        palette = MobdColorPalette(self.AnimationIndex, self.FrameIndex)
        palette.ReadPalette(data, paletteOffset - fileOffset)

        image = MobdImage(self.AnimationIndex, self.FrameIndex)
        image.ReadImage(data, imageOffset - fileOffset, flags)

        # MobdFrame.__CheckImage(image, palette)

        return image, palette
    
    # @staticmethod
    # def __CheckImage(image : MobdImage, palette : MobdColorPalette) -> None:
    #     """ Do some plausebility checks with the image data.
    #     """
    #     colors = palette.ColorsRgb
    #     for pixel in image.Pixels:
    #         if pixel < 0 or pixel >= len(colors):
    #             raise Exception("Image invalid pixel data")

    def __ReadPointList(self, data : bytearray, position : int) -> list[ModbPoint]:
        """ Reads a list of points from the raw data.

        Args:
            data (bytearray): The raw data buffer.
            position (int): The position of the pointlist in the raw data buffer.

        Returns:
            list[ModbPoint]: The pointlist read from the raw data.
        """
        MobdFileStructure[position] = f"Point list animation {self.AnimationIndex:03} frame {self.FrameIndex:03}"

        pointList : list[ModbPoint] = []

        while True:
            boxId = GetUInt32LE(data, position)
            if boxId == 0xFFFFFFFF:
                break
            
            point = ModbPoint()
            position = point.ReadPoint(data, position)
            pointList.append(point)

        return pointList
    
    def __ReadBoxList(self, data : bytearray, position : int) -> None:
        MobdFileStructure[position] = f"Box list animation {self.AnimationIndex:03} frame {self.FrameIndex:03}"

        # TODO: read the boxes ???
        pass
        # tst1 = GetUInt32LE(data, position + 0)
        # tst2 = GetUInt32LE(data, position + 4)
        # tst3 = GetUInt32LE(data, position + 8)
        # tst4 = GetUInt32LE(data, position + 12)


class MobdAnimation:
    """ This class represents an animation that consists of a list of frames.
    """

    FrameList : list[MobdFrame]
    IsRotationalAnimation : bool = False
    AnimationNumber : int
    AnimationHeader : int
    AnimationEnd : int

    def __init__(self, animationNumber : int) -> None:
        self.FrameList = []
        self.AnimationNumber = animationNumber
    
    def GetMaxWidthAndHeight(self) -> tuple[int, int]:
        """ Calculates the maximum width and height of the images in the animation.

        Returns:
            tuple[int, int]: Maximum width and height in pixels.
        """
        width = 0
        height = 0

        for frame in self.FrameList:
            width = max(width, frame.Image.Width)
            height = max(height, frame.Image.Height)

        return width, height
    
    def ReadAnimation(self, data : bytearray, position : int, fileOffset : int) -> tuple[int, int]:
        """ Read one animation from the data file.

        Args:
            data (bytearray): The raw data of the MOBD file.
            position (int): The position(=offset) of the animation in the data file.
            fileOffset (int): The offset of the MOBD file in the file container.

        Returns:
            tuple[int, bool]: Position after this animation, True if animation is valid.
        """
        MobdFileStructure[position] = f"MobdAnimation {self.AnimationNumber:03}"

        self.FrameList = []

        # 1. animation header: format is 0xCCBBAA00 (animation speed???)
        self.AnimationHeader = GetUInt32LE(data, position)
        position += 4

        # print(f"Animation header: 0x{self.AnimationHeader:08X}")

        # 2. list of frame offsets terminated by 0 or -1 (0xFFFFFFFF)
        #       0xFFFFFFFF = more animations follow
        #       0x00000000 = no further animations

        fileLength = len(data)
        frameCount = 0
        framePosition = GetUInt32LE(data, position)
        offsetFirstFrame = 0xFFFFFFFF

        while (framePosition != 0) and (framePosition != 0xFFFFFFFF):
            
            # frame position is counted from file container start, so we need to correct it
            framePositionCorrected = framePosition - fileOffset
            if (framePositionCorrected < 0) or (framePositionCorrected >= fileLength):
                raise Exception(f"Invalid frame position: {framePosition} (0x{framePosition:08X}) corrected: {framePositionCorrected} (0x{framePositionCorrected:08X})")
            
            frame = MobdFrame(self.AnimationNumber, frameCount)
            frame.ReadFrame(data, framePositionCorrected, fileOffset)
            frameCount += 1
            offsetFirstFrame = min(offsetFirstFrame, framePositionCorrected)

            self.FrameList.append(frame)

            position += 4
            framePosition = GetUInt32LE(data, position)

        # 3. animation end: 0 = repeat, 0xFFFFFFFF = do not repeat (???)
        self.AnimationEnd = GetUInt32LE(data, position)
        position += 4

        # print(f"Animation end: 0x{self.AnimationEnd:08X} Number of frames: {frameCount}")

        # if frameCount == 0:
        #     raise Exception("Error, no frames in animation!")

        return position, offsetFirstFrame

class MobdFile:
    """ This class represents the contents of a MOBD file.
        A MOBD file consists of animations.
    """

    AnimationList : list[MobdAnimation]

    def __init__(self, file : ContainerFile | None = None) -> None:
        self.AnimationList = []

        if file is not None:
            self.ReadAnimations(file.RawData, file.FileOffset)
    
    def ReadAnimations(self, data : bytearray, fileOffset : int) -> None:
        """ Reads animations from a MOBD file.

        Args:
            data (bytearray): The raw data of the MOBD file.
            fileOffset (int): The offset of the MOBD file in the file container.
        """

        """
        MOBD file format:
        4 bytes     e.g. 0x10000000     Animation header
        4 bytes     e.g. 1344           Offset of the first animation frame + fileOffset
        ...
        4 bytes     0xFFFFFFFF          end of animation
        ...
        4 bytes     0x00000000          no further animations
        """
        global MobdFileStructure
        MobdFileStructure = {}
        MobdColorPalette.MobdColorPalettes = {}

        animationNumber = 0
        position = 0
        offsetFirstFrame = 0xFFFFFFFF
        value = GetUInt32LE(data, position)

        animationOffsetDict : dict[int, MobdAnimation] = {}

        while (value & 0xFF000000) != 0:
            if position >= offsetFirstFrame:
                print(f"WARNING: Invalid position for animation: First frame: {offsetFirstFrame} current position: {position}")
                break
            
            animationOffset = position

            animation = MobdAnimation(animationNumber)
            position, animationOffsetFirstFrame = animation.ReadAnimation(data, position, fileOffset)

            if len(animation.FrameList) > 0:
                # print(f"Animation {animationNumber}")
                self.AnimationList.append(animation)
                animationOffsetDict[animationOffset] = animation
                offsetFirstFrame = min(offsetFirstFrame, animationOffsetFirstFrame)
                animationNumber += 1

            value = GetUInt32LE(data, position)

        # the animation is a rotational animation if the animation offset is listed in the data block
        # between the last animation and the first frame,
        # otherwise it is a simple animation
        while position < offsetFirstFrame:
            value = GetUInt32LE(data, position)
            position += 4
            if value == 0:
                continue
            
            offset = value - fileOffset
            if offset in animationOffsetDict:
                animationOffsetDict[offset].IsRotationalAnimation = True

        MobdFileStructure[len(data)] = f"MobdFile size"


        
