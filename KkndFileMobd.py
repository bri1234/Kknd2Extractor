# -*- coding: utf-8 -*-

from DataBuffer import GetInt32LE, GetUInt32LE, GetUInt16LE, GetUInt8, GetStringReverse

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

class MobdPalette:

    Colors : list[int]

    def __init__(self) -> None:
        self.Colors = []

    def ReadPalette(self, data : bytearray, palettePosition : int, fileOffset : int) -> None:

        self.Colors = []
        numColors = GetUInt16LE(data, palettePosition + 12)
        colorPosition = palettePosition + 14

        for _ in range(numColors):
            color16 = GetUInt16LE(data, colorPosition)
            colorPosition += 2

            red = ((color16 & 0x7C00) >> 7) & 0xFF
            green = ((color16 & 0x03E0) >> 2) & 0xFF
            blue = ((color16 & 0x001F) << 3) & 0xFF

            color24 = (red << 16) | (green << 8) | blue
            self.Colors.append(color24)

class MobdImage:

    Width : int = 0
    Height : int = 0
    Pixels : bytearray

    def __init__(self) -> None:
        self.Pixels = bytearray()

    def ReadImage(self, data : bytearray, imagePosition : int, flags : int) -> None:
        self.Pixels = bytearray()

        self.Width = GetInt32LE(data, imagePosition + 0)
        self.Height = GetInt32LE(data, imagePosition + 4)

        isFlipped = (flags & (1 << 31)) != 0
        isCompressed = (flags & (1 << 27)) != 0
        has256Colors = (flags & (1 << 26)) != 0

        pixelDataPosition = imagePosition + 8

        if isCompressed:
            self.Pixels = MobdImage.Decompress(data, pixelDataPosition, self.Width, self.Height, has256Colors)
        else:
            self.Pixels = data[pixelDataPosition : pixelDataPosition + self.Width * self.Height]

        if isFlipped:
            self.Pixels = MobdImage.FlipPixels(self.Pixels, self.Width, self.Height)

    @staticmethod
    def Decompress(data : bytearray, pixelDataPosition : int, width : int, height : int, has256Colors : bool) -> bytearray:

        size = width * height
        pixels = bytearray()
        line = bytearray()
        position = pixelDataPosition

        while len(pixels) < size:

            # decompress one row
            
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
                line.clear()
                pixelCount = compressedSize - 0x80

                for _ in range(pixelCount):
                    twoPixels = GetUInt8(data, position)
                    position += 1

                    # store first pixel
                    line.append((twoPixels & 0xF0) >> 4)

                    # store second pixel
                    if len(line) < width:
                        line.append(twoPixels & 0x0F)
                
                if len(line) != width:
                    raise Exception(f"MobdImage: invalid row size: {len(line)} (width = {width})")
                
                pixels.extend(line)

            else:
                line.clear()
                
                lineEndOffset = position + compressedSize
                while position < lineEndOffset:
                    chunkSize = GetUInt8(data, position)
                    position += 1

                    if chunkSize < 0x80:
                        line.extend([0] * chunkSize)
                    else:
                        pixelCount = chunkSize - 0x80

                        if has256Colors:
                            byteArray = data[position : position + pixelCount]
                            position += pixelCount
                            line.extend(byteArray)

                        else:
                            numBytes = pixelCount // 2 + pixelCount % 2

                            for idx in range(numBytes):
                                twoPixels = GetUInt8(data, position)
                                position += 1

                                line.append((twoPixels & 0xF0) >> 4)

                                if (idx + 1 < numBytes) or (pixelCount % 2 == 0):
                                    line.append(twoPixels & 0x0F)

                if len(line) != width:
                    raise Exception(f"MobdImage: invalid row size: {len(line)} (width = {width})")
                
                pixels.extend(line)
        
        return pixels
    
    @staticmethod
    def FlipPixels(pixels : bytearray, width : int, height : int) -> bytearray:

        flippedPixels = bytearray()

        for rowIdx in range(height):
            row = pixels[rowIdx * width : (rowIdx + 1) * width]
            row.reverse()

            flippedPixels.extend(row)

        return flippedPixels

class MobdFrame:
    """ This is one frame of the animation.
    """

    # The sprite offset from the center point of the image:
    # SpriteOffsetX = width / 2 - x
    # SpriteOffsetY = height / 2 - y
    OffsetX : int = 0
    OffsetY : int = 0

    PointList : list[ModbPoint]
    Palette : MobdPalette
    Image : MobdImage

    def __init__(self) -> None:
        self.PointList = []
        self.Palette = MobdPalette()
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
            self.Image, self.Palette = MobdFrame.__ReadRenderFlags(data, renderFlagsOffset - fileOffset, fileOffset)

        if boxListOffset > 0:
            MobdFrame.__ReadBoxList(data, boxListOffset - fileOffset)

    @staticmethod
    def __ReadRenderFlags(data : bytearray, position : int, fileOffset : int) -> tuple[MobdImage, MobdPalette]:
        frameType = GetStringReverse(data, position + 0, 4)
        if frameType != "SPNS" and frameType != "SPRC":
            raise Exception(f"Invalid frame format: {frameType}")
        
        flags = GetUInt32LE(data, position + 4)
        paletteOffset = GetUInt32LE(data, position + 8)
        imageOffset = GetUInt32LE(data, position + 12)

        palette = MobdPalette()
        palette.ReadPalette(data, paletteOffset - fileOffset, fileOffset)

        image = MobdImage()
        image.ReadImage(data, imageOffset - fileOffset, flags)

        return image, palette
    
    @staticmethod
    def __ReadPointList(data : bytearray, position : int) -> list[ModbPoint]:
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

    def __init__(self, animationNumber : int) -> None:
        self.FrameList = []
        self.AnimationNumber = animationNumber
    
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
        animationHeader = GetUInt32LE(data, position)
        position += 4

        print(f"Animation header: 0x{animationHeader:08X}")

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
        animationEnd = GetUInt32LE(data, position)
        position += 4

        print(f"Animation end: 0x{animationEnd:08X} Number of frames: {frameCount}")

        # if frameCount == 0:
        #     raise Exception("Error, no frames in animation!")

        return position, offsetFirstFrame

class Mobd:
    """ This class represents the contents of a MOBD file.
        A MOBD file consists of animatations.
    """

    AnimationList : list[MobdAnimation]

    def __init__(self) -> None:
        self.AnimationList = []
    
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
        4 bytes     0x00000000          no firther animations
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
                print(f"Animation {animationNumber}")
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
        


