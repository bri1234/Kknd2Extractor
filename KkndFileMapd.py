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

from KkndFileCompression import UncompressFile
from KkndFileContainer import ReadFileTypeList
from DataBuffer import GetStringReverse, GetUInt32LE, GetUInt16LE

class MapdColorPalette:
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
        numberOfColors = GetUInt32LE(data, palettePosition)
        colorPosition = palettePosition + 4

        for _ in range(numberOfColors):
            color16 = GetUInt16LE(data, colorPosition)
            colorPosition += 2

            red = ((color16 & 0x7C00) >> 7) & 0xFF
            green = ((color16 & 0x03E0) >> 2) & 0xFF
            blue = ((color16 & 0x001F) << 3) & 0xFF

            color24 = (red << 16) | (green << 8) | blue
            self.Colors.append(color24)

class MapdTile:
    """ This class stores the pixel data of a tile.
    """

    # The image pixel data. A Pixel is an index in the color palette.
    Pixels : bytearray

    def __init__(self) -> None:
        self.Pixels = bytearray()

    def ReadTile(self, fileData : bytearray, tileOffset : int, tileWidth : int, tileHeight : int) -> None:
        self.Pixels = fileData[tileOffset : tileOffset + tileWidth * tileHeight]

class MapdLayer:
    """ This class stores the tiles of a layer.
        A layer consists of small tiles.
    """

    TileWidthInPixels : int = 0
    TileHeightInPixels : int = 0
    MapWidthInTiles : int = 0
    MapHeightInTiles : int = 0
    MapWidthInPixels : int = 0
    MapHeightInPixels : int = 0

    # The tiles that build the layer.
    TileMap : list[int]

    # List of tile data.
    TileList : dict[int, MapdTile]

    def __init__(self) -> None:
        self.TileMap : list[int] = []
        self.TileList : dict[int, MapdTile] = {}

    def ReadLayer(self, fileData : bytearray, fileOffset : int, layerOffset : int) -> None:
        """ Reads the layer data.

        Args:
            fileData (bytearray): The raw file data.
            fileOffset (int): The offset of the file in the container.
            layerOffset (int): The offset of the layer in the file.
        """
        self.__ReadLayerHeader(fileData, layerOffset)
        self.__ReadLayerTiles(fileData, fileOffset, layerOffset + 32)

    def __ReadLayerTiles(self, fileData : bytearray, fileOffset : int, tilesOffset : int) -> None:
        """ Read all tiles of the layer.

        Args:
            fileData (bytearray): _description_
            fileOffset (int): _description_
            tilesOffset (int): _description_
        """
        numberOfTiles = self.MapWidthInTiles * self.MapHeightInTiles
        pos = tilesOffset

        self.TileMap = []
        self.TileList = {}

        for _ in range(numberOfTiles):
            tileOffset = GetUInt32LE(fileData, pos) & 0xFFFFFFFC
            pos += 4

            self.TileMap.append(tileOffset)

            if tileOffset == 0:
                continue

            if tileOffset not in self.TileList:
                tile = MapdTile()
                tile.ReadTile(fileData, tileOffset - fileOffset, self.TileWidthInPixels, self.TileHeightInPixels)
                self.TileList[tileOffset] = tile

    def __ReadLayerHeader(self, fileData : bytearray, layerOffset : int) -> None:
        """ Reads the layer header information.

        Args:
            fileData (bytearray): The raw file data.
            layerOffset (int): The offset of the layer in the file.
        """
        magicStr = GetStringReverse(fileData, layerOffset, 4)
        if magicStr != "SCRL":
            raise Exception(f"Not a MAPD layer. Missing 'SCRL'.")

        self.TileWidthInPixels = GetUInt32LE(fileData, layerOffset + 4)
        self.TileHeightInPixels = GetUInt32LE(fileData, layerOffset + 8)
        self.MapWidthInTiles = GetUInt32LE(fileData, layerOffset + 12)
        self.MapHeightInTiles = GetUInt32LE(fileData, layerOffset + 16)
        self.MapWidthInPixels = GetUInt32LE(fileData, layerOffset + 20)
        self.MapHeightInPixels = GetUInt32LE(fileData, layerOffset + 24)

        if self.MapWidthInPixels != self.TileWidthInPixels * self.MapWidthInTiles:
            raise Exception(f"Error map width is invalid!")

        if self.MapHeightInPixels != self.TileHeightInPixels * self.MapHeightInTiles:
            raise Exception(f"Error map height is invalid!")

class MapdFile:
    """ This class stores the color palette and the layers for the map.
    """

    # a list with the layers
    LayerList : list[MapdLayer]

    # the color palette of the layers
    ColorPalette : MapdColorPalette

    def __init__(self) -> None:
        self.LayerList = []
        self.ColorPalette = MapdColorPalette()
        
    def ReadMapdFile(self, fileData : bytearray, fileOffset : int) -> None:
        """ Reads the map layers and color palette from the MAPD file.

        Args:
            fileData (bytearray): The raw MAPD file data.
            fileOffset (int): The offset of the MAPD file in the file container.
        """
        self.LayerList = []
        pos = 4

        # read the MAPD file header
        numberOfLayers = GetUInt32LE(fileData, pos)
        pos += 4

        layerOffsetList : list[int] = []
        for _ in range(numberOfLayers):
            layerOffset = GetUInt32LE(fileData, pos)
            pos += 4

            layerOffsetList.append(layerOffset)

        # read the color palette
        self.ColorPalette = MapdColorPalette()
        self.ColorPalette.ReadPalette(fileData, pos)

        # read the layers
        for idx in range(numberOfLayers):
            layer = MapdLayer()
            layer.ReadLayer(fileData, fileOffset, layerOffsetList[idx] - fileOffset)
            self.LayerList.append(layer)

def ReadMaps(fileName : str) -> list[MapdFile]:
    """ Reads all MAPD files from a KKND2 asset file container.

    Args:
        fileName (str): The name of the KNND2 asset file.

    Returns:
        list[MapdFile]: List of MAPD files.
    """

    data, _, _ = UncompressFile(fileName)
    mapdFileList : list[MapdFile] = []

    fileTypeList, _ = ReadFileTypeList(data)
    for fileType in fileTypeList:
        if fileType.FileType != "MAPD":
            continue
        
        for file in fileType.FileList:
            mapdFile = MapdFile()
            mapdFile.ReadMapdFile(file.RawData, file.FileOffset)
            mapdFileList.append(mapdFile)

    return mapdFileList

def __Test() -> None:
    mapdFiles = ReadMaps("assets/multiplayermap/mlti_01.lpm")

if __name__ == "__main__":
    __Test()
