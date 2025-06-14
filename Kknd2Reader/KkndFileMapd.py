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
from Kknd2Reader.KkndFileCompression import UncompressFile
from Kknd2Reader.KkndFileContainer import ReadFileTypeList
from Kknd2Reader.DataBuffer import GetStringReverse, GetUInt32LE, GetUInt16LE
from Kknd2Reader.TerrainAttributes import ETerrainAttribute

class MapdColorPalette:
    """ This class stores the color palette.
    """

    # 4 byte RGB color
    ColorsRGB : list[int]
    ColorsBGR : list[int]

    def __init__(self) -> None:
        self.ColorsRGB = []
        self.ColorsBGR = []

    def ReadPalette(self, data : bytearray, palettePosition : int) -> None:
        """ Reads the color palette from the KKN2 data and stores it internally as a list of RGB values.

        Args:
            data (bytearray): The raw KKND2 data.
            palettePosition (int): The position of the color palette in the data buffer.
        """

        self.ColorsRGB = []
        self.ColorsBGR = []
        numberOfColors = GetUInt32LE(data, palettePosition)
        colorPosition = palettePosition + 4

        for _ in range(numberOfColors):
            color16 = GetUInt16LE(data, colorPosition)
            colorPosition += 2

            red = ((color16 & 0x7C00) >> 7) & 0xFF
            green = ((color16 & 0x03E0) >> 2) & 0xFF
            blue = ((color16 & 0x001F) << 3) & 0xFF

            colorRgb = (red << 16) | (green << 8) | blue
            colorBgr = (blue << 16) | (green << 8) | red

            self.ColorsRGB.append(colorRgb)
            self.ColorsBGR.append(colorBgr)

class MapdTile:
    """ This class stores the pixel data of a tile.
    """

    # The image pixel data. A Pixel is an index in the color palette.
    Pixels : bytearray

    # the tile width in pixels
    Width : int

    # the tile height in pixels
    Height : int

    # the rendered tile as numpyarray
    TileImage : npt.NDArray[np.uint32]

    def __init__(self, widthInPixels : int = 0, heightInPixels : int = 0) -> None:
        """ Creates a new tile.

        Args:
            width (int, optional): The tile width in pixels. Defaults to 0.
            height (int, optional): The tile height in pixels. Defaults to 0.
        """
        self.Pixels = bytearray(widthInPixels * heightInPixels)
        self.Width = widthInPixels
        self.Height = heightInPixels

    def GetPixel(self, column : int, row : int) -> int:
        """ Returns one pixel.

        Args:
            x (int): Pixel column in the image.
            y (int): Pixel row in the image.

        Returns:
            int: The pixel = Index in the color palette.
        """
        return self.Pixels[column + row * self.Width]
    
    def ReadTile(self, fileData : bytearray, tileOffset : int, tileWidth : int, tileHeight : int) -> None:
        """ Reads the tile from raw data.

        Args:
            fileData (bytearray): The raw file data.
            tileOffset (int): The tile offset in the file data.
            tileWidth (int): The tile width in pixels.
            tileHeight (int): The tile height in pixels.
        """
        self.Width = tileWidth
        self.Height = tileHeight
        self.Pixels = fileData[tileOffset : tileOffset + tileWidth * tileHeight]

    def RenderTileUInt32Abgr(self, colorPalette : MapdColorPalette) -> None:
        """ Renders the tile as ABGR data.
        """

        colorsBgr = colorPalette.ColorsBGR
        pixels = np.zeros((self.Width, self.Height), np.uint32)
        pixelIdx = 0

        for tilePixelRow in range(self.Height):
            for tilePixelColumn in range(self.Width):
                pixel = self.Pixels[pixelIdx]
                pixelIdx += 1
                if pixel >= len(colorsBgr):
                    raise Exception(f"Can not render imager, invalid pixel value: {pixel}")

                # pixel is transparent if pixel value is 0
                
                pixelAbgrColor = (colorsBgr[pixel] | 0xFF000000) if pixel != 0 else 0x00000000
                pixels[tilePixelColumn, tilePixelRow] = pixelAbgrColor

        self.TileImage = pixels

class MapdTerrainAttributes:
    """ This class stores the terrain attributes for the layer tiles.
    """

    # Map and Layer width in tiles
    MapWidthInTiles : int

    # Map and Layer height in tiles
    MapHeightInTiles : int

    # The terrain attributes of the layer tiles
    TerrainAttributes : list[ETerrainAttribute]

    def __init__(self) -> None:
        self.MapWidthInTiles = 0
        self.MapHeightInTiles = 0
        self.TerrainAttributes = []

    def GetTerrainAttribute(self, column : int, row : int) -> ETerrainAttribute:
        """ Returns the terrain attribute for a position.

        Args:
            column (int): The column in number of tiles.
            row (int): The row in number of tiles.

        Returns:
            ETerrainAttribute: The terrain attribute.
        """
        return self.TerrainAttributes[column + row * self.MapWidthInTiles]

    def ReadTerrainAttributes(self, fileData : bytearray, terrainAttributesOffset : int, mapWidthInTiles : int, mapHeightInTiles : int) -> None:
        """ Reads the terrain attributes from the raw data.

        Args:
            fileData (bytearray): The raw file data.
            terrainAttributesOffset (int): The offset of the terrain data in the raw file data.
            mapWidthInTiles (int): Layer or map width in number of tiles.
            mapHeightInTiles (int): Layer or map height in number of tiles.
        """

        self.MapWidthInTiles = mapWidthInTiles
        self.MapHeightInTiles = mapHeightInTiles
        self.TerrainAttributes = []

        numberOfTiles = mapWidthInTiles * mapHeightInTiles

        for idx in range(numberOfTiles):
            terrainAttribute = fileData[terrainAttributesOffset + idx]
            self.TerrainAttributes.append( ETerrainAttribute(terrainAttribute) )

class MapdLayer:
    """ This class stores the tiles of a layer.
        A layer consists of small tiles.
    """

    # Tile width in pixels
    TileWidthInPixels : int

    # Tile height in pixels
    TileHeightInPixels : int

    # Map and Layer width in tiles
    MapWidthInTiles : int

    # Map and Layer height in tiles
    MapHeightInTiles : int

    # Map and Layer width in pixels
    MapWidthInPixels : int

    # Map and Layer height in pixels
    MapHeightInPixels : int

    # The tiles that build the layer.
    TileMap : list[int]

    # List of tile data.
    TileList : dict[int, MapdTile]

    TerrainAttributes : MapdTerrainAttributes

    def __init__(self) -> None:
        self.TileMap = []
        self.TileList = {}
        self.TerrainAttributes = MapdTerrainAttributes()

        self.TileWidthInPixels = 0
        self.TileHeightInPixels = 0
        self.MapWidthInTiles = 0
        self.MapHeightInTiles = 0
        self.MapWidthInPixels = 0
        self.MapHeightInPixels = 0

    def GetTile(self, tileColumn : int, tileRow : int) -> MapdTile:
        """ Returns the tile at the position.

        Args:
            tileColumn (int): The tile column.
            tileRow (int): The tile row.

        Returns:
            MapdTile: The tile at the position.
        """
        tileId = self.TileMap[tileColumn + tileRow * self.MapWidthInTiles]
        return self.TileList[tileId]
    
    def ReadLayer(self, fileData : bytearray, fileOffset : int, layerOffset : int) -> None:
        """ Reads the layer data.

        Args:
            fileData (bytearray): The raw file data.
            fileOffset (int): The offset of the file in the container.
            layerOffset (int): The offset of the layer in the file.
        """
        self.__ReadLayerHeader(fileData, layerOffset)
        self.__ReadTerrainAttributes(fileData, fileOffset, layerOffset)
        self.__ReadLayerTiles(fileData, fileOffset, layerOffset + 32)

    def __ReadTerrainAttributes(self, fileData : bytearray, fileOffset : int, layerOffset : int) -> None:
        """ Reads the terrain aatributes from the data file.

        Args:
            fileData (bytearray): The raw file data.
            fileOffset (int): The offset of the file in the container.
            layerOffset (int): The offset of the layer in the file.
        """
        terrainAttributesOffset = GetUInt32LE(fileData, layerOffset + 28)

        self.TerrainAttributes.ReadTerrainAttributes(fileData, terrainAttributesOffset - fileOffset,
                                                     self.MapWidthInTiles, self.MapHeightInTiles)

    def __ReadLayerTiles(self, fileData : bytearray, fileOffset : int, tilesOffset : int) -> None:
        """ Read all tiles of the layer.

        Args:
            fileData (bytearray): The raw file data.
            fileOffset (int): The offset of the file in the container.
            tilesOffset (int): The offset of the tile data.
        """
        numberOfTiles = self.MapWidthInTiles * self.MapHeightInTiles
        pos = tilesOffset

        self.TileMap = []
        self.TileList = {}

        # add empty tile
        self.TileList[0] = MapdTile(self.TileWidthInPixels, self.TileHeightInPixels)

        for _ in range(numberOfTiles):
            tileOffset = GetUInt32LE(fileData, pos) & 0xFFFFFFFC
            pos += 4

            self.TileMap.append(tileOffset)

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
        
    def RenderImageUInt32Abgr(self, colorPalette : MapdColorPalette) -> npt.NDArray[np.uint32]:
        """ Renders the layer as ABGR data.

        Returns:
            npt.NDArray[np.uint32]: The layer ARGB data in a 2D array [Width, Height].
        """

        for tile in self.TileList.values():
            tile.RenderTileUInt32Abgr(colorPalette)

        pixels = np.zeros((self.MapWidthInPixels, self.MapHeightInPixels), np.uint32)
        tileWidth = self.TileWidthInPixels
        tileHeight = self.TileHeightInPixels
        
        for tileRow in range(self.MapHeightInTiles):
            layerPixelRow = tileRow * tileHeight

            for tileColumn in range(self.MapWidthInTiles):
                layerPixelColumn = tileColumn * tileWidth
                tile = self.GetTile(tileColumn, tileRow)

                pixels[layerPixelColumn : layerPixelColumn + tileWidth, layerPixelRow : layerPixelRow + tileHeight] = tile.TileImage

        return pixels

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

            MapdFile.__CheckImage(layer, self.ColorPalette)

    @staticmethod
    def __CheckImage(layer : MapdLayer, palette : MapdColorPalette) -> None:
        """ Do some plausebility checks with the image data.
        """
        colors = palette.ColorsRGB

        for tile in layer.TileList.values():
            for pixel in tile.Pixels:
                if pixel < 0 or pixel >= len(colors):
                    raise Exception("Image invalid pixel data")
            
    def RenderLayerUint32Abgr(self, layerIndex : int) -> npt.NDArray[np.uint32]:
        """ Renders the layer as ABGR color data.

        Args:
            layerIndex (int): The layer with the index in the list of layers to be rendered.

        Returns:
            npt.NDArray[np.uint32]: The layer RGB data in a 2D array [Width, Height].
        """
        return self.LayerList[layerIndex].RenderImageUInt32Abgr(self.ColorPalette)

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

