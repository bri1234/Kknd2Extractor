# -*- coding: utf-8 -*-

from DataBuffer import GetInt32LE, GetUInt32LE, GetString

# for debugging: list of animation headers
AnimationHeaders : dict[int, int] = {}

def CountAnimationHeader(header : int) -> None:
    """ For debugging: count animation header IDs.
    
    Args:
        data (bytearray): The raw data of the MOBD file.
        fileOffset (int): The offset of the MOBD file in the file container.
    """
    global AnimationHeaders

    if header in AnimationHeaders:
        AnimationHeaders[header] += 1
    else:
        AnimationHeaders[header] = 1

class ModbPoint:
    """ This class represents one point.
    """

    Id : int

    Px : int
    Py : int
    Pz : int    # unused

    def ReadPoint(self, data : bytearray, position : int) -> int:
        """ Reads one point from the raw data.

        Args:
            data (bytearray): The raw data of the MOBD file.
            position (int): The position(=offset) of the point in the MOBD file.

        Returns:
            int: The position after this point.
        """

        self.Id = GetUInt32LE(data, position + 0)

        self.Px = GetInt32LE(data, position + 4) >> 8
        self.Py = GetInt32LE(data, position + 8) >> 8
        self.Pz = GetInt32LE(data, position + 12) >> 8

        return position + 16

class MobdFrame:
    """ This is one frame of the animation.
    """

    # The sprite offset from the center point of the image:
    # SpriteOffsetX = width / 2 - x
    # SpriteOffsetY = height / 2 - y
    OffsetX : int
    OffsetY : int

    PointList : list[ModbPoint]

    def __init__(self) -> None:
        self.PointList = []
    
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
            MobdFrame.__ReadRenderFlags(data, renderFlagsOffset - fileOffset)

        if boxListOffset > 0:
            MobdFrame.__ReadBoxList(data, boxListOffset - fileOffset)

    @staticmethod
    def __ReadRenderFlags(data : bytearray, position : int) -> None:
        frameType = GetString(data, position + 0, 4)
        flags = GetUInt32LE(data, position + 4)
    
    @staticmethod
    def __ReadBoxList(data : bytearray, position : int) -> None:
        tst1 = GetUInt32LE(data, position + 0)
        tst2 = GetUInt32LE(data, position + 4)
        tst3 = GetUInt32LE(data, position + 8)
        tst4 = GetUInt32LE(data, position + 12)

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

class MobdAnimation:
    """ This class represents an animation that consists of a list of frames.
    """

    FrameList : list[MobdFrame]
    IsRotationalAnimation : bool = False
    
    def __init__(self) -> None:
        self.FrameList = []
    
    def ReadAnimation(self, data : bytearray, position : int, fileOffset : int) -> tuple[int, int]:
        """ Read one animation from the data file.

        Args:
            data (bytearray): The raw data of the MOBD file.
            position (int): The position(=offset) of the animation in the data file.
            fileOffset (int): The offset of the MOBD file in the file container.

        Returns:
            tuple[int, bool]: Position after this animation, True if animation is valid.
        """

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

            position += 4
            framePosition = GetUInt32LE(data, position)

        # 3. animation end: 0 = repeat, 0xFFFFFFFF = do not repeat (???)
        animationEnd = GetUInt32LE(data, position)
        position += 4

        print(f"Animation end: 0x{animationEnd:08X} Number of frames: {frameCount}")

        if frameCount == 0:
            raise Exception("Error, no frames in animation!")

        CountAnimationHeader(animationHeader)

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

        position = 0
        offsetFirstFrame = 0xFFFFFFFF
        value = GetUInt32LE(data, position)

        animationOffsetDict : dict[int, MobdAnimation] = {}

        while value != 0:
            if position >= offsetFirstFrame:
                raise Exception(f"Invalid position for animation: First frame: {offsetFirstFrame} current position: {position}")
            
            animationOffset = position

            animation = MobdAnimation()
            position, animationOffsetFirstFrame = animation.ReadAnimation(data, position, fileOffset)

            self.AnimationList.append(animation)
            animationOffsetDict[animationOffset] = animation
            offsetFirstFrame = min(offsetFirstFrame, animationOffsetFirstFrame)

            value = GetUInt32LE(data, position)

        # the animation is a rotational animation if the animation offset is listed in the data block
        # between the last animation and the first frame
        while position < offsetFirstFrame:
            value = GetUInt32LE(data, position)
            position += 4
            if value == 0:
                continue
            
            offset = value - fileOffset
            if offset in animationOffsetDict:
                animationOffsetDict[offset].IsRotationalAnimation = True
        


