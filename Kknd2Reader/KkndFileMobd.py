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

    # 4 byte RGB color
    Colors : list[int]

    def __init__(self) -> None:
        self.Colors = []

    def GetColorsBytearray(self) -> bytearray:
        """ Converts the colors into a byte array.

        Returns:
            bytearray: The colors as little endian byte array.
        """
        b = bytearray()

        for color in self.Colors:
            b.extend(color.to_bytes(4, "little"))

        return b
    
    def ReadPalette(self, data : bytearray, palettePosition : int) -> None:
        """ Reads the color palette from the KKN2 data and stores it internally as a list of RGB values.

        Args:
            data (bytearray): The raw KKND2 data.
            palettePosition (int): The position of the color palette in the data buffer.
        """

        self.Colors = []
        numberOfColors = GetUInt16LE(data, palettePosition + 12)
        colorPosition = palettePosition + 14

        for _ in range(numberOfColors):
            color16 = GetUInt16LE(data, colorPosition)
            colorPosition += 2

            red = ((color16 & 0x7C00) >> 7) & 0xFF
            green = ((color16 & 0x03E0) >> 2) & 0xFF
            blue = ((color16 & 0x001F) << 3) & 0xFF

            color24 = (red << 16) | (green << 8) | blue
            self.Colors.append(color24)

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
        has256Colors = (flags & (1 << 26)) != 0

        pixelDataPosition = imagePosition + 8

        if isCompressed:
            self.Pixels = MobdImage.__DecompressImageData(data, pixelDataPosition, self.Width, self.Height, has256Colors)
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

    def __init__(self) -> None:
        self.PointList = []
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

    def RenderImageUInt32(self) -> npt.NDArray[np.uint32]:
        """ Renders the image as RGB data in a numpy array.

        Returns:
            npt.NDArray[np.uint32]: The image RGB data in a 2D array [Width, Height].
        """

        img = self.Image
        colors = self.ColorPalette.Colors
        pixelsOutput = np.zeros((img.Width, img.Height), np.uint32)

        for row in range(img.Height):
            for column in range(img.Width):
                pixel = img.GetPixel(column, row)
                
                pixelColor = colors[pixel] if pixel >= 0 and pixel < len(colors) else 0
                pixelsOutput[column, row] = pixelColor

        return pixelsOutput
    
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
        if frameType != "SPNS" and frameType != "SPRC":
            raise Exception(f"Invalid frame format: {frameType}")
        
        flags = GetUInt32LE(data, position + 4)
        paletteOffset = GetUInt32LE(data, position + 8)
        imageOffset = GetUInt32LE(data, position + 12)

        palette = MobdColorPalette()
        palette.ReadPalette(data, paletteOffset - fileOffset)

        image = MobdImage()
        image.ReadImage(data, imageOffset - fileOffset, flags)

        MobdFrame.__CheckImage(image, palette)

        return image, palette
    
    @staticmethod
    def __CheckImage(image : MobdImage, palette : MobdColorPalette) -> None:
        """ Do some plausebility checks with the image data.
        """
        colors = palette.Colors
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
        


