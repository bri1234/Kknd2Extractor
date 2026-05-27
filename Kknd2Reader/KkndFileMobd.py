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
from Kknd2Reader import KkndPalette
from typing import Any
import colorsys

MobdFileStructure : dict[int, str] = {}

FactionNameById : dict[int, str] = {
    0: "Survivors",
    1: "Mutants",
    2: "Series9",
}

FactionIdByJsonPrefix : dict[str, int] = {
    "S": 0,
    "M": 1,
    "R": 2,
}

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

def GetFactionIdFromMobdIndex(mobdIndex : int) -> int | None:
    """Returns the faction id for a MOBD index according to the table found in Kknd2.exe.
    """

    if 178 <= mobdIndex <= 251:
        return 0
    
    if 26 <= mobdIndex <= 96:
        return 1
    
    if 106 <= mobdIndex <= 177:
        return 2
    
    return None

def GetFactionIdFromMobdName(mobdName : str) -> int | None:
    """Returns the faction id from the optional gamesprt.lpk.json name.
    """

    prefix = mobdName.split("_", 1)[0]
    return FactionIdByJsonPrefix.get(prefix)

def GetFactionIdFromMobdFile(file : ContainerFile) -> int | None:
    """Returns the faction id for a MOBD file.

    The EXE table uses MOBD indices as the primary source. The optional JSON
    name is used only as a fallback for files outside the confirmed ranges.
    """

    factionId = GetFactionIdFromMobdIndex(file.Index)
    if factionId is not None:
        return factionId
    
    return GetFactionIdFromMobdName(file.FileName)

def GetFactionName(factionId : int | None) -> str | None:
    """Returns the faction name for a faction id.
    """

    if factionId is None:
        return None
    
    return FactionNameById.get(factionId)

def GetRequiredTeamPaletteName(maxPixelValue : int, has256Colors : bool) -> str:
    """Returns the external team palette name required for the image indices.
    """

    if has256Colors or maxPixelValue >= 64:
        return "spriteb.pal"
    
    return "spritet.pal"

LocalTeamPaletteName = "local-team-palette"

def IsAirMobdName(mobdFileName : str) -> bool:
    """Returns whether a MOBD name belongs to an aircraft sprite.
    """

    return "_A_" in mobdFileName

def IsInfantryMobdName(mobdFileName : str) -> bool:
    """Returns whether a MOBD name belongs to an infantry sprite.
    """

    return "_I_" in mobdFileName

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

    # the number of colors stored in the local MOBD palette
    NumberOfColors : int

    def __init__(self, animationIndex : int, frameIndex : int) -> None:
        self.ColorsRgb = []
        self.ColorsBgr = []
        self.AnimationIndex = animationIndex
        self.FrameIndex = frameIndex
        self.NumberOfColors = 0

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
        self.NumberOfColors = numberOfColors

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
    def ConvertRgb15To24(color15 : int) -> int:
        """ Converts a 15 bit RGB value to a 24 bit RGB value.

        Args:
            color15 (int): 15 RGB value (5 bit per color channel)

        Returns:
            int: 24 RGB value (8 bit per color channel)
        """
        red   = ((color15 & 0x7C00) >> 7) & 0xFF
        green = ((color15 & 0x03E0) >> 2) & 0xFF
        blue  = ((color15 & 0x001F) << 3) & 0xFF

        return (red << 16) | (green << 8) | blue
    
    @staticmethod
    def ConvertRgb24To15(color24 : int) -> int:
        """ Converts a 24 bit RGB value to a 15 bit RGB value.

        Args:
            color24 (int): 24 RGB value (8 bit per color channel)

        Returns:
            int: 15 RGB value (5 bit per color channel)
        """
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

    # the MOBD file index in gamesprt.lpk
    MobdFileIndex : int | None

    # the optional MOBD file name from gamesprt.lpk.json
    MobdFileName : str

    # faction information derived from the Kknd2.exe MOBD table
    FactionId : int | None
    FactionName : str | None

    # palette/team-color information derived from image indices and local palette size
    MaxPixelValue : int
    LocalPaletteColorCount : int
    NeedsExternalPalette : bool
    UsesTeamPaletteIndexSpace : bool
    RequiredTeamPaletteName : str | None
    CanUseTeamPalette : bool

    def __init__(self, animationIndex : int, frameIndex : int, mobdFileIndex : int | None = None, mobdFileName : str = "", factionId : int | None = None) -> None:
        self.Pixels = bytearray()
        self.AnimationIndex = animationIndex
        self.FrameIndex = frameIndex
        self.MobdFileIndex = mobdFileIndex
        self.MobdFileName = mobdFileName
        self.FactionId = factionId
        self.FactionName = GetFactionName(factionId)
        self.MaxPixelValue = 0
        self.LocalPaletteColorCount = 0
        self.NeedsExternalPalette = False
        self.UsesTeamPaletteIndexSpace = False
        self.RequiredTeamPaletteName = None
        self.CanUseTeamPalette = False

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

        self.MaxPixelValue = max(self.Pixels) if len(self.Pixels) > 0 else 0

    def UpdateTeamPaletteInfo(self, palette : MobdColorPalette) -> None:
        """Updates whether this image can be rendered with a faction/team palette.

        The EXE uses faction-specific palette blocks. Frames with pixel indices
        outside the local MOBD palette need one of those external palettes.
        """

        self.LocalPaletteColorCount = palette.NumberOfColors
        self.NeedsExternalPalette = self.MaxPixelValue >= self.LocalPaletteColorCount
        usesLocalTeamPalette = not self.Has256Colors and not self.NeedsExternalPalette and IsAirMobdName(self.MobdFileName) and self.LocalPaletteColorCount >= 128
        usesSpriteTeamPalette = not self.Has256Colors and not self.NeedsExternalPalette and IsInfantryMobdName(self.MobdFileName)
        self.UsesTeamPaletteIndexSpace = self.Has256Colors or self.NeedsExternalPalette or usesLocalTeamPalette or usesSpriteTeamPalette
        self.RequiredTeamPaletteName = None

        if usesLocalTeamPalette:
            self.RequiredTeamPaletteName = LocalTeamPaletteName
        elif usesSpriteTeamPalette:
            self.RequiredTeamPaletteName = "spritet.pal"
        elif self.UsesTeamPaletteIndexSpace:
            self.RequiredTeamPaletteName = GetRequiredTeamPaletteName(self.MaxPixelValue, self.Has256Colors)

        self.CanUseTeamPalette = self.FactionId is not None and self.UsesTeamPaletteIndexSpace

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

    # the MOBD file index in gamesprt.lpk
    MobdFileIndex : int | None

    # the optional MOBD file name from gamesprt.lpk.json
    MobdFileName : str

    # faction information derived from the Kknd2.exe MOBD table
    FactionId : int | None
    FactionName : str | None

    def __init__(self, animationIndex : int, frameIndex : int, mobdFileIndex : int | None = None, mobdFileName : str = "", factionId : int | None = None) -> None:
        self.PointList = []
        self.Bitmap = None
        self.ColorPalette = MobdColorPalette(animationIndex, frameIndex)
        self.Image = MobdImage(animationIndex, frameIndex, mobdFileIndex, mobdFileName, factionId)
        self.AnimationIndex = animationIndex
        self.FrameIndex = frameIndex
        self.MobdFileIndex = mobdFileIndex
        self.MobdFileName = mobdFileName
        self.FactionId = factionId
        self.FactionName = GetFactionName(factionId)
    
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

    def RenderFrameUInt32Abgr(self, teamColorId : int | None = 0) -> npt.NDArray[np.uint32]:
        """ Renders the tile as ABGR data.

        teamColorId=None renders with the local MOBD palette.
        """

        img = self.Image
        colorsBgr = self.__GetRenderColorsBgr(teamColorId)
        pixels = np.zeros((img.Width, img.Height), np.uint32)
        unknownPixels : dict[int, int] = {}

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

                pixels[column, row] = pixelAbgrColor
        
        if len(unknownPixels) > 0:
            print("Unknown pixels:")
            for pixelValue in unknownPixels.keys():
                print(f"pixel {pixelValue}: count {unknownPixels[pixelValue]}")
            pass

        return pixels

    def GetRenderColorsRgb(self, teamColorId : int | None = 0) -> list[int]:
        """Returns the RGB palette used for rendering or exporting this frame.

        teamColorId=None returns the local MOBD palette.
        """

        img = self.Image

        if teamColorId is None or not img.CanUseTeamPalette or img.FactionId is None:
            return self.ColorPalette.ColorsRgb
        
        if img.RequiredTeamPaletteName == LocalTeamPaletteName:
            return self.__GetLocalTeamColorsRgb(teamColorId)

        return KkndPalette.get_team_palette_rgb(img.FactionId, teamColorId, img.RequiredTeamPaletteName)

    def GetRenderColorsRgbBytearray(self, teamColorId : int | None = 0) -> bytearray:
        """Returns the render palette as little endian RGB byte array.
        """

        b = bytearray()

        for color in self.GetRenderColorsRgb(teamColorId):
            b.extend(color.to_bytes(4, "little"))

        return b

    def __GetRenderColorsBgr(self, teamColorId : int | None = 0) -> list[int]:
        """Returns the palette used for rendering this frame.
        """

        img = self.Image

        if teamColorId is None or not img.CanUseTeamPalette or img.FactionId is None:
            return self.ColorPalette.ColorsBgr
        
        if img.RequiredTeamPaletteName == LocalTeamPaletteName:
            return ConvertColorsFromRgbToBgr(self.__GetLocalTeamColorsRgb(teamColorId))

        return KkndPalette.get_team_palette_bgr(img.FactionId, teamColorId, img.RequiredTeamPaletteName)

    def __GetLocalTeamColorsRgb(self, teamColorId : int) -> list[int]:
        """Returns the 16-color team block from the local MOBD palette.
        """

        start = teamColorId * 16
        end = start + 16

        if start < 0 or end > len(self.ColorPalette.ColorsRgb):
            return self.ColorPalette.ColorsRgb

        return self.ColorPalette.ColorsRgb[start:end]

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

        image = MobdImage(self.AnimationIndex, self.FrameIndex, self.MobdFileIndex, self.MobdFileName, self.FactionId)
        image.ReadImage(data, imageOffset - fileOffset, flags)
        image.UpdateTeamPaletteInfo(palette)

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

    # the MOBD file index in gamesprt.lpk
    MobdFileIndex : int | None

    # the optional MOBD file name from gamesprt.lpk.json
    MobdFileName : str

    # faction information derived from the Kknd2.exe MOBD table
    FactionId : int | None
    FactionName : str | None

    def __init__(self, animationNumber : int, mobdFileIndex : int | None = None, mobdFileName : str = "", factionId : int | None = None) -> None:
        self.FrameList = []
        self.AnimationNumber = animationNumber
        self.MobdFileIndex = mobdFileIndex
        self.MobdFileName = mobdFileName
        self.FactionId = factionId
        self.FactionName = GetFactionName(factionId)
    
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
            
            frame = MobdFrame(self.AnimationNumber, frameCount, self.MobdFileIndex, self.MobdFileName, self.FactionId)
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

    # the MOBD file index in gamesprt.lpk
    MobdFileIndex : int | None

    # the optional MOBD file name from gamesprt.lpk.json
    MobdFileName : str

    # faction information derived from the Kknd2.exe MOBD table
    FactionId : int | None
    FactionName : str | None

    def __init__(self, file : ContainerFile | None = None) -> None:
        self.AnimationList = []
        self.MobdFileIndex = None
        self.MobdFileName = ""
        self.FactionId = None
        self.FactionName = None

        if file is not None:
            self.MobdFileIndex = file.Index
            self.MobdFileName = file.FileName
            self.FactionId = GetFactionIdFromMobdFile(file)
            self.FactionName = GetFactionName(self.FactionId)
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

            animation = MobdAnimation(animationNumber, self.MobdFileIndex, self.MobdFileName, self.FactionId)
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


        
