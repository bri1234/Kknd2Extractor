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

from termcolor import cprint

import numpy as np
import numpy.typing as npt
from Kknd2Reader.DataBuffer import GetInt32LE, GetUInt32LE, GetUInt16LE, GetUInt8, GetStringReverse
from Kknd2Reader.KkndFileContainer import ContainerFile
from typing import Any

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

    # 4 byte RGB color palette for Survivors buildings
    ColorsSurvivorsBuildingsRgb = [0x0000FF00,0x00100909,0x00181810,0x00101020,0x00101820,0x00101831,0x00102020,0x00102931,0x00182039,0x00201008,0x00201808,0x00291808,0x00201818,0x00291810,0x00311810,0x00202010,0x00292010,0x00292910,0x00312008,0x00392900,0x00312010,0x00312910,0x00312918,0x00392010,0x00392910,0x00392918,0x00313118,0x00393118,0x00292020,0x00292929,0x00202939,0x00293139,0x00393129,0x00393939,0x0010204A,0x00203141,0x0029394A,0x0029315A,0x00393952,0x0029316A,0x00313973,0x00314162,0x0039416A,0x00314A73,0x0039526A,0x00412014,0x00412910,0x00412918,0x004A2910,0x004A2918,0x00413118,0x004A3110,0x004A3118,0x004A3918,0x00522918,0x00523110,0x00523118,0x00523918,0x005A3918,0x00413120,0x00413920,0x00413929,0x004A3920,0x004A3929,0x00523120,0x005A3120,0x00623918,0x00623120,0x00623920,0x006A3920,0x006A3939,0x00733929,0x00414110,0x004A5218,0x004A4120,0x004A4129,0x00524129,0x00524A29,0x005A4A29,0x00524A31,0x00525A20,0x005A5231,0x005A5239,0x00624118,0x006A4118,0x00734A18,0x006A5229,0x00625231,0x006A5A39,0x00734129,0x00734A20,0x00734A29,0x00735A31,0x007B5231,0x00626220,0x007B6A20,0x00736239,0x007B6239,0x00737329,0x00414141,0x00414A52,0x004A525A,0x00524A4A,0x005A5252,0x00414A62,0x00414A73,0x00415A73,0x0052526A,0x005A5A73,0x00625A41,0x00625A62,0x00736241,0x007B6A4A,0x006A6A6A,0x00737373,0x007F7F7F,0x0031418B,0x00394183,0x00415283,0x004A5A8B,0x005A5A83,0x004A6283,0x004A6A8B,0x00416294,0x0052628B,0x005A6A83,0x00526A9C,0x005A73A4,0x006A7383,0x00627394,0x00737B83,0x006A73A4,0x005A7BC5,0x004A838B,0x005A83A4,0x00738394,0x006A83A4,0x006283B4,0x007B83B0,0x007394AC,0x006A8BC5,0x007B83CD,0x007B8BC5,0x007394CD,0x007B94DE,0x00738BEE,0x007BA4C5,0x00832920,0x00836A39,0x008B6239,0x00837339,0x009C5858,0x00837352,0x00837B52,0x00947B4A,0x008B835A,0x0094835A,0x0083837B,0x009C8B62,0x00A48B62,0x00AC946A,0x00A49473,0x00AC9C73,0x00BD9C62,0x00B49C73,0x00B4A47B,0x00BDA473,0x00C5AC7B,0x00CDB47B,0x00D5BD7B,0x00838394,0x00838B9C,0x008B9C9C,0x00948B83,0x00949494,0x009C9C9C,0x00838BAC,0x008394BD,0x009CA4BD,0x00A4AC9C,0x00ACA4A4,0x00B4B4B4,0x00BDBDBD,0x00839CDE,0x00839CEE,0x008BA4C5,0x008BACDE,0x0083B4CD,0x008BBDDE,0x009CBDCD,0x0083A4F6,0x008BB4F6,0x009CBDF6,0x00B4BDDE,0x00A4ACF6,0x00ACB4F6,0x0094CDEE,0x009CD5F6,0x00B4C5F6,0x00B4DEF6,0x00A4E6F6,0x00BDEEF6,0x00CDB483,0x00D5BD83,0x00DEC583,0x00E6CD83,0x00E6CD8B,0x00F6D58B,0x00F6DE9C,0x00F6EE9C,0x00F6F6A4,0x00F6F6AC,0x00C5C5C5,0x00CDCDCD,0x00D5D5D5,0x00DEDEDE,0x00DEE6F6,0x00D5F6F6,0x00F6CDCD,0x00F6F6CD,0x00E6E6E6,0x00F6F6EE,0x00005AFF,0x0000AEFF,0x0000FFFF,0x00FFFFFF,0x00FFFF00,0x00FFC000,0x00FF8A00,0x00FF5400,0x00622929,0x00834141,0x009C4A4A,0x00AC5252,0x00BD6262,0x00CD6A6A,0x00E67373,0x00FF7B7B,0x00FF8383,0x00FF8B8B,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000]

    # 4 byte RGB color palette for Series 9 buildings
    # Red
    # ColorsSeries9BuildingsRgb=[0x00000000,0x00000400,0x00080C08,0x00080C08,0x00101410,0x00101410,0x00181C18,0x00181C18,0x00212421,0x00212421,0x00292C29,0x00292421,0x00292C29,0x00313431,0x00312C29,0x00313431,0x00393C39,0x00393431,0x00393C39,0x00424542,0x00424542,0x00424542,0x004A4D4A,0x004A4D4A,0x00525552,0x00524D4A,0x00525552,0x00525552,0x005A5D5A,0x005A5D5A,0x00636563,0x00635D5A,0x00636563,0x00636563,0x006B6D6B,0x006B6563,0x006B6D6B,0x006B6D6B,0x00737573,0x00737573,0x007B7D7B,0x007B7D7B,0x007B7D7B,0x00848684,0x00847D7B,0x00848684,0x008C8E8C,0x008C8E8C,0x008C8E8C,0x00949694,0x00949694,0x009C9E9C,0x009C9E9C,0x00A5A6A5,0x00A5A6A5,0x00ADAEAD,0x00AD9694,0x00ADAEAD,0x00ADAEAD,0x00B5B6B5,0x00B5AEAD,0x00B5B6B5,0x00BDBEBD,0x00BDBEBD,0x00C6C7C6,0x00C6C7C6,0x00CECFCE,0x00CECFCE,0x00D6D7D6,0x00D6D7D6,0x00DEDFDE,0x00DEDFDE,0x00E7E7E7,0x00E7E7E7,0x00EFEFEF,0x00000000,0x00FFFFFF,0x008C867B,0x00393429,0x0084756B,0x006B655A,0x0073655A,0x00080400,0x00423C31,0x00524D42,0x005A5542,0x00635542,0x007B756B,0x00A59684,0x00522421,0x005A2421,0x006B2421,0x00632C31,0x00732C29,0x007B2C31,0x007B3C39,0x008C3439,0x008C3C39,0x008C3439,0x00943431,0x009C3C42,0x008C3C42,0x009C3C42,0x00AD3C42,0x00AD3C39,0x00B53C42,0x00B54542,0x00BD4552,0x00C64D52,0x00C6454A,0x00AD454A,0x00B54D52,0x00C64D52,0x00BD5D6B,0x00C64D52,0x00C6555A,0x00CE4D52,0x00CE4D5A,0x00D65563,0x00D65D63,0x00DE4D5A,0x00DE555A,0x00DE4D52,0x00F75563,0x00EF5D6B,0x00F75D6B,0x00FF5563,0x00FF5D6B,0x00FF5D5A,0x00FF5D63,0x00FF756B,0x00FF7D73,0x00FF7584,0x00FF7D7B,0x00FF9694,0x00FF9E9C,0x00292C29,0x00393C39,0x00424539,0x004A4D42,0x00848684,0x00101C18,0x00293431,0x00313431,0x00424542,0x00424D4A,0x004A5552,0x006B7573,0x00737D7B,0x007B8684,0x00000000,0x007B8684,0x00A5AEAD,0x00A5AEAD,0x00000000,0x00000000,0x00000000,0x0042E7F7,0x0042EFF7,0x004AF7FF,0x0039C7D6,0x0039CFDE,0x005ADFE7,0x00738684,0x00848E94,0x008C969C,0x0094A6A5,0x00A5AEB5,0x00ADB6BD,0x007B8684,0x006B7573,0x006B757B,0x00848E94,0x0094A6AD,0x0052555A,0x00000418,0x00181C21,0x00212429,0x00292C29,0x00212429,0x00313431,0x00313439,0x00393C39,0x00393C42,0x0042454A,0x004A4D52,0x00525552,0x0052555A,0x005A5D63,0x00636563,0x0063656B,0x006B6D6B,0x00737573,0x00848684,0x006B6D84,0x0084868C,0x008C8E8C,0x0073758C,0x00949694,0x0094969C,0x009C9E9C,0x00A5A6AD,0x00ADAEAD,0x00ADAEB5,0x00393C52,0x00312C4A,0x00211C31,0x009486B5,0x00AD96C6,0x00392C4A,0x005A556B,0x00634D84,0x0052455A,0x0063656B,0x007B757B,0x00181C18,0x00393439,0x00424542,0x004A454A,0x004A4D4A,0x005A555A,0x00736D73,0x00737573,0x00FFFFFF,0x00000000,0x00000000,0x007B5531,0x00000000,0x00734D21,0x00634518,0x004A3C21,0x00312C18,0x00635531,0x006B5D39,0x004A4529,0x00524D29,0x00000000,0x00636521,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00422400,0x00291C00,0x00100C00,0x00423410,0x004A3C18,0x00292408,0x00312C08,0x00393410,0x00000000,0x00000000,0x00000000]
    # Green
    ColorsSeries9BuildingsRgb=[0x00000000,0x00000400,0x00080C08,0x00080C08,0x00101410,0x00101410,0x00181C18,0x00181C18,0x00212421,0x00212421,0x00292C29,0x00292421,0x00292C29,0x00313431,0x00312C29,0x00313431,0x00393C39,0x00393431,0x00393C39,0x00424542,0x00424542,0x00424542,0x004A4D4A,0x004A4D4A,0x00525552,0x00524D4A,0x00525552,0x00525552,0x005A5D5A,0x005A5D5A,0x00636563,0x00635D5A,0x00636563,0x00636563,0x006B6D6B,0x006B6563,0x006B6D6B,0x006B6D6B,0x00737573,0x00737573,0x007B7D7B,0x007B7D7B,0x007B7D7B,0x00848684,0x00847D7B,0x00848684,0x008C8E8C,0x008C8E8C,0x008C8E8C,0x00949694,0x00949694,0x009C9E9C,0x009C9E9C,0x00A5A6A5,0x00A5A6A5,0x00ADAEAD,0x00AD9694,0x00ADAEAD,0x00ADAEAD,0x00B5B6B5,0x00B5AEAD,0x00B5B6B5,0x00BDBEBD,0x00BDBEBD,0x00C6C7C6,0x00C6C7C6,0x00CECFCE,0x00CECFCE,0x00D6D7D6,0x00D6D7D6,0x00DEDFDE,0x00DEDFDE,0x00E7E7E7,0x00E7E7E7,0x00EFEFEF,0x00000000,0x00FFFFFF,0x008C867B,0x00393429,0x0084756B,0x006B655A,0x0073655A,0x00080400,0x00423C31,0x00524D42,0x005A5542,0x00635542,0x007B756B,0x00A59684,0x00001400,0x00082408,0x00082C08,0x00102410,0x00103410,0x00183C18,0x00213C21,0x00214D21,0x00214D21,0x00214D21,0x00214D21,0x00295529,0x00294D29,0x00295D29,0x00316531,0x00296531,0x00316D31,0x00316D31,0x00397539,0x00397539,0x00397D39,0x00396539,0x00396D39,0x00427542,0x0052754A,0x00427D42,0x004A7D4A,0x00428642,0x00428642,0x00528E52,0x00528E52,0x004A8E4A,0x004A8E4A,0x004A964A,0x0052A652,0x005A9E5A,0x005AA65A,0x0052AE5A,0x0063B663,0x005AB663,0x0063B663,0x006BB67B,0x0073B67B,0x007BB67B,0x007BB684,0x0094B69C,0x009CB69C,0x00292C29,0x00393C39,0x00424539,0x004A4D42,0x00848684,0x00101C18,0x00293431,0x00313431,0x00424542,0x00424D4A,0x004A5552,0x006B7573,0x00737D7B,0x007B8684,0x00000000,0x007B8684,0x00A5AEAD,0x00A5AEAD,0x00000000,0x00000000,0x00000000,0x0042E7F7,0x0042EFF7,0x004AF7FF,0x0039C7D6,0x0039CFDE,0x005ADFE7,0x00738684,0x00848E94,0x008C969C,0x0094A6A5,0x00A5AEB5,0x00ADB6BD,0x007B8684,0x006B7573,0x006B757B,0x00848E94,0x0094A6AD,0x0052555A,0x00000418,0x00181C21,0x00212429,0x00292C29,0x00212429,0x00313431,0x00313439,0x00393C39,0x00393C42,0x0042454A,0x004A4D52,0x00525552,0x0052555A,0x005A5D63,0x00636563,0x0063656B,0x006B6D6B,0x00737573,0x00848684,0x006B6D84,0x0084868C,0x008C8E8C,0x0073758C,0x00949694,0x0094969C,0x009C9E9C,0x00A5A6AD,0x00ADAEAD,0x00ADAEB5,0x00393C52,0x00312C4A,0x00211C31,0x009486B5,0x00AD96C6,0x00392C4A,0x005A556B,0x00634D84,0x0052455A,0x0063656B,0x007B757B,0x00181C18,0x00393439,0x00424542,0x004A454A,0x004A4D4A,0x005A555A,0x00736D73,0x00737573,0x00FFFFFF,0x00000000,0x00000000,0x007B5531,0x00000000,0x00734D21,0x00634518,0x004A3C21,0x00312C18,0x00635531,0x006B5D39,0x004A4529,0x00524D29,0x00000000,0x00636521,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00422400,0x00291C00,0x00100C00,0x00423410,0x004A3C18,0x00292408,0x00312C08,0x00393410,0x00000000,0x00000000,0x00000000]
    # Blue
    # ColorsSeries9BuildingsRgb=[0x00000000,0x00000400,0x00080C08,0x00080C08,0x00101410,0x00101410,0x00181C18,0x00181C18,0x00212421,0x00212421,0x00292C29,0x00292421,0x00292C29,0x00313431,0x00312C29,0x00313431,0x00393C39,0x00393431,0x00393C39,0x00424542,0x00424542,0x00424542,0x004A4D4A,0x004A4D4A,0x00525552,0x00524D4A,0x00525552,0x00525552,0x005A5D5A,0x005A5D5A,0x00636563,0x00635D5A,0x00636563,0x00636563,0x006B6D6B,0x006B6563,0x006B6D6B,0x006B6D6B,0x00737573,0x00737573,0x007B7D7B,0x007B7D7B,0x007B7D7B,0x00848684,0x00847D7B,0x00848684,0x008C8E8C,0x008C8E8C,0x008C8E8C,0x00949694,0x00949694,0x009C9E9C,0x009C9E9C,0x00A5A6A5,0x00A5A6A5,0x00ADAEAD,0x00AD9694,0x00ADAEAD,0x00ADAEAD,0x00B5B6B5,0x00B5AEAD,0x00B5B6B5,0x00BDBEBD,0x00BDBEBD,0x00C6C7C6,0x00C6C7C6,0x00CECFCE,0x00CECFCE,0x00D6D7D6,0x00D6D7D6,0x00DEDFDE,0x00DEDFDE,0x00E7E7E7,0x00E7E7E7,0x00EFEFEF,0x00000000,0x00FFFFFF,0x008C867B,0x00393429,0x0084756B,0x006B655A,0x0073655A,0x00080400,0x00423C31,0x00524D42,0x005A5542,0x00635542,0x007B756B,0x00A59684,0x00181C31,0x00212439,0x00212C4A,0x00292C42,0x00293452,0x00313C5A,0x0039455A,0x0039456B,0x00424D6B,0x0039456B,0x00394573,0x00424D7B,0x00424D6B,0x004A557B,0x004A5584,0x004A558C,0x00525D94,0x00525D94,0x005A6594,0x005A659C,0x005A65A5,0x00526584,0x005A6D94,0x005A6D9C,0x006B7D94,0x00636DA5,0x006B75A5,0x005A6DAD,0x006375AD,0x00737DAD,0x007386AD,0x006B7DB5,0x006B7DB5,0x006B75BD,0x007386CE,0x007B8EC6,0x007B8ECE,0x00738ED6,0x008496E7,0x007B8EE7,0x008496E7,0x009496E7,0x009496E7,0x00A5AEE7,0x00A5A6E7,0x00BDBEE7,0x00CECFE7,0x00292C29,0x00393C39,0x00424539,0x004A4D42,0x00848684,0x00101C18,0x00293431,0x00313431,0x00424542,0x00424D4A,0x004A5552,0x006B7573,0x00737D7B,0x007B8684,0x00000000,0x007B8684,0x00A5AEAD,0x00A5AEAD,0x00000000,0x00000000,0x00000000,0x0042E7F7,0x0042EFF7,0x004AF7FF,0x0039C7D6,0x0039CFDE,0x005ADFE7,0x00738684,0x00848E94,0x008C969C,0x0094A6A5,0x00A5AEB5,0x00ADB6BD,0x007B8684,0x006B7573,0x006B757B,0x00848E94,0x0094A6AD,0x0052555A,0x00000418,0x00181C21,0x00212429,0x00292C29,0x00212429,0x00313431,0x00313439,0x00393C39,0x00393C42,0x0042454A,0x004A4D52,0x00525552,0x0052555A,0x005A5D63,0x00636563,0x0063656B,0x006B6D6B,0x00737573,0x00848684,0x006B6D84,0x0084868C,0x008C8E8C,0x0073758C,0x00949694,0x0094969C,0x009C9E9C,0x00A5A6AD,0x00ADAEAD,0x00ADAEB5,0x00393C52,0x00312C4A,0x00211C31,0x009486B5,0x00AD96C6,0x00392C4A,0x005A556B,0x00634D84,0x0052455A,0x0063656B,0x007B757B,0x00181C18,0x00393439,0x00424542,0x004A454A,0x004A4D4A,0x005A555A,0x00736D73,0x00737573,0x00FFFFFF,0x00000000,0x00000000,0x007B5531,0x00000000,0x00734D21,0x00634518,0x004A3C21,0x00312C18,0x00635531,0x006B5D39,0x004A4529,0x00524D29,0x00000000,0x00636521,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00422400,0x00291C00,0x00100C00,0x00423410,0x004A3C18,0x00292408,0x00312C08,0x00393410,0x00000000,0x00000000,0x00000000]

    # 4 byte RGB color palette for Evolved buildings
    ColorsEvolvedBuildingsRgb=[0x0000FB00,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x00000000,0x0000FFFF,0x0000F6F6,0x0000EEEE,0x0000E6E6,0x0000DEDE,0x0000D5D5,0x0000CDCD,0x0000C5C5,0x00FBE3F3,0x00EBAAEB,0x00E392E3,0x00613161,0x00CA79D2,0x00AA59B2,0x008A419A,0x0020E3FB,0x008AF3FB,0x0000FBFB,0x00B2FBFB,0x00518259,0x00E3FBE3,0x008AC28A,0x00395128,0x00C2FB49,0x00FBFB41,0x00FBFBCA,0x00FBFBDB,0x00595900,0x00393931,0x00FBF3A2,0x00B2A200,0x00FBE328,0x00FBE359,0x00FBEBAA,0x00F3EBCA,0x00F3DB8A,0x00FBC220,0x00F3CA59,0x00F3B208,0x00715100,0x00FBDB92,0x00F3DBA2,0x00BA8208,0x00AA7100,0x00312818,0x00CA8A20,0x00927139,0x008A7149,0x00594118,0x00FBA220,0x00F3C279,0x00D29A49,0x00BA9A69,0x00AA8A59,0x008A5910,0x00715120,0x00695941,0x00594931,0x00FBCA8A,0x00D2AA71,0x00796141,0x00FBAA49,0x00EB9220,0x009A7951,0x00E37900,0x00BA6100,0x00B27128,0x008A6131,0x00824908,0x00EB7908,0x00BAA28A,0x009A8A79,0x00695139,0x00613910,0x00614120,0x00513920,0x00514131,0x00493928,0x00413120,0x00201810,0x00F38A28,0x00C28249,0x00392008,0x00FBBA9A,0x00201008,0x00392820,0x00925139,0x00824128,0x00FBA28A,0x008A4939,0x00715149,0x00280800,0x00B26151,0x00A25949,0x00693931,0x00512820,0x00411810,0x00EB7169,0x00FBFBFB,0x00DBDBDB,0x00D50000,0x00C2C2C2,0x00B0B0B0,0x009F9F9F,0x008E8E8E,0x007C7C7C,0x006B6B6B,0x005A5A5A,0x00494949,0x00494949,0x00202020,0x00000000,0x00FB6161,0x00FB2020,0x00FB0000,0x00DBD4FB,0x00E5A1A1,0x00FB7171,0x00FF5151,0x00ED1515,0x00CF0F0F,0x00B20B0B,0x00950707,0x00780404,0x005B0202,0x003E0000,0x00000000]

    # 4 byte RGB color read from MOBD file
    # this color palette is not valid for buildings
    ColorsRgb : list[int]

    # 4 byte BGR color read from MOBD file
    # this color palette is not valid for buildings
    ColorsBgr : list[int]

    def __init__(self) -> None:
        self.ColorsRgb = []
        self.ColorsBgr = []

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

        self.ColorsRgb = []
        self.ColorsBgr = []
        numberOfColors = GetUInt16LE(data, palettePosition + 12)
        colorPosition = palettePosition + 14

        for _ in range(numberOfColors):
            color16 = GetUInt16LE(data, colorPosition)
            colorPosition += 2

            red = ((color16 & 0x7C00) >> 7) & 0xFF
            green = ((color16 & 0x03E0) >> 2) & 0xFF
            blue = ((color16 & 0x001F) << 3) & 0xFF

            self.ColorsRgb.append((red << 16) | (green << 8) | blue)
            self.ColorsBgr.append((blue << 16) | (green << 8) | red)

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

    def __init__(self) -> None:
        self.Pixels = bytearray()

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

    def __init__(self) -> None:
        self.PointList = []
        self.Bitmap = None
        self.ColorPalette = MobdColorPalette()
        self.Image = MobdImage()
    
    def ReadFrame(self, data : bytearray, framePosition : int, fileOffset : int) -> None:
        """ Reads one frame from the animation.

        Args:
            data (bytearray): The raw data of the MOBD file.
            framePosition (int): The position(=offset) of the frame in the MOBD file.
        """
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
            self.PointList = MobdFrame.__ReadPointList(data, pointListOffset - fileOffset)

        if renderFlagsOffset > 0:
            self.Image, self.ColorPalette = MobdFrame.__ReadImageAndColorPalette(data, renderFlagsOffset - fileOffset, fileOffset)

        if boxListOffset > 0:
            MobdFrame.__ReadBoxList(data, boxListOffset - fileOffset)

    def RenderFrameUInt32Abgr(self) -> npt.NDArray[np.uint32]:
        """ Renders the tile as ABGR data.
        """

        img = self.Image
        colorsBgr = self.ColorPalette.ColorsBgr
        pixels = np.zeros((img.Width, img.Height), np.uint32)
        unknownPixels : dict[int, int] = {}

        colorsBgr = ConvertColorsFromRgbToBgr(MobdColorPalette.ColorsSeries9BuildingsRgb)

        # print(f"# colors: {len(colorsBgr)}")

        for row in range(img.Height):
            for column in range(img.Width):
                pixel = img.GetPixel(column, row)

                if pixel >= len(colorsBgr):
                    # might be used to colorize the sprites???
                    # raise Exception(f"Can not render imager, invalid pixel value: {pixel}")
                    pixelAbgrColor = 0xFF00FF00 | (pixel & 0xFF)
                    # pixelAbgrColor = 0xFF00BBBB
                    # pixelAbgrColor = 0xFF000000 | colorsBgrSeries9[pixel]

                    unknownPixels[pixel] = unknownPixels[pixel] + 1 if pixel in unknownPixels else 1

                else:
                    # pixel is transparent if pixel value is 0
                    pixelAbgrColor = (colorsBgr[pixel] | 0xFF000000) if pixel != 0 else 0x00000000

                pixels[column, row] = pixelAbgrColor
        
        if len(unknownPixels) > 0:
            print("Unknown pixels:")
            for pixel in unknownPixels.keys():
                print(f"pixel {pixel}: count {unknownPixels[pixel]}")

        return pixels

    @staticmethod
    def __ReadImageAndColorPalette(data : bytearray, position : int, fileOffset : int) -> tuple[MobdImage, MobdColorPalette]:
        """ Reads the image and the color palette from the raw data.

        Args:
            data (bytearray): The raw data buffer.
            position (int): The position of the image and color palette in the raw data buffer.
            fileOffset (int): The offset of the image file in the file container.

        Returns:
            tuple[MobdImage, MobdPalette]: The image and the color palette.
        """
        frameType = GetStringReverse(data, position + 0, 4)
        if frameType != "SPRC" and frameType != "SPNS":
            raise Exception(f"Invalid frame format: {frameType}")
        
        flags = GetUInt32LE(data, position + 4)
        paletteOffset = GetUInt32LE(data, position + 8)
        imageOffset = GetUInt32LE(data, position + 12)

        palette = MobdColorPalette()
        palette.ReadPalette(data, paletteOffset - fileOffset)

        image = MobdImage()
        image.ReadImage(data, imageOffset - fileOffset, flags)

        # MobdFrame.__CheckImage(image, palette)

        return image, palette
    
    @staticmethod
    def __CheckImage(image : MobdImage, palette : MobdColorPalette) -> None:
        """ Do some plausebility checks with the image data.
        """
        colors = palette.ColorsRgb
        for pixel in image.Pixels:
            if pixel < 0 or pixel >= len(colors):
                raise Exception("Image invalid pixel data")

    @staticmethod
    def __ReadPointList(data : bytearray, position : int) -> list[ModbPoint]:
        """ Reads a list of points from the raw data.

        Args:
            data (bytearray): The raw data buffer.
            position (int): The position of the pointlist in the raw data buffer.

        Returns:
            list[ModbPoint]: The pointlist read from the raw data.
        """
        pointList : list[ModbPoint] = []

        while True:
            boxId = GetUInt32LE(data, position)
            if boxId == 0xFFFFFFFF:
                break
            
            point = ModbPoint()
            position = point.ReadPoint(data, position)
            pointList.append(point)

        return pointList
    
    @staticmethod
    def __ReadBoxList(data : bytearray, position : int) -> None:
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
            
            frame = MobdFrame()
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
        


