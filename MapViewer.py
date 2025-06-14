# type: ignore

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

import wx
import wx.lib.scrolledpanel as wxls

import os
import threading
from pathlib import Path

import Kknd2Reader.KkndFileMapd as mapd
import Kknd2Reader.TerrainAttributes as ta
import Kknd2Reader.KkndFileCplc as cplc
import Kknd2Reader.PrettyJson as pjson
from Kknd2Reader.KkndCreatureLib import CreatureLibrary

class FrameMain(wx.Frame):
    """ The main window.
    """

    __creatureLibrary : CreatureLibrary | None

    BitmapBottom : wx.Bitmap
    BitmapTop : wx.Bitmap
    BitmapAttributes : wx.Bitmap
    BitmapEntities : wx.Bitmap

    def __init__(self):
        super().__init__(None, title = "KKND2 Map Viewer", size = (1000, 800))

        terrainIconsPath = os.path.join("Kknd2Reader", "TerrainAttributeIcons.png")
        creatureLibPath = os.path.join("assets", "creature.klb")

        self.__terrainAttributeIconList = FrameMain.__LoadTerrainAttributeIcons(terrainIconsPath)
        self.__creatureLibrary = FrameMain.__LoadCreatureLib(creatureLibPath)

        self.__CreateMenuBar()
        self.__CreateWidgets()

    @staticmethod
    def __LoadTerrainAttributeIcons(fileName : str) -> list[wx.Bitmap]:
        """ Reads the terrain attribute icons that are stored in one PNG file.

        Args:
            fileName (str): The name of the PNG file with the terrain attribute icons.

        Returns:
            list[wx.Bitmap]: The terrain aatribute icons.
        """
        terrainAttributeIcons = wx.Bitmap(fileName)
        terrainAttributeIconList : list[wx.Bitmap] = []

        for idx in range(36):
            icon = terrainAttributeIcons.GetSubBitmap(wx.Rect(idx * 32, 0, 32, 32))
            terrainAttributeIconList.append(icon)

        return terrainAttributeIconList

    @staticmethod
    def __LoadCreatureLib(fileName : str) -> CreatureLibrary | None:
        """ Loads the creature library if the file exists.

        Args:
            fileName (str): The creature library filename and path.

        Returns:
            CreatureLibrary | None: The creature library.
        """
        
        if not os.path.isfile(fileName):
            return None

        creatureLib = CreatureLibrary()
        creatureLib.ReadLibraryFile(fileName)
        return creatureLib

    def __CreateWidgets(self) -> None:
        """ Creates the GUI.
        """
        panel = wx.Panel(self)

        scrollPanel = wxls.ScrolledPanel(panel, -1, style = wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        scrollPanel.SetAutoLayout(1)
        scrollPanel.SetupScrolling()

        self.__imageControl = wx.StaticBitmap(scrollPanel)

        scrollPanelSizer = wx.BoxSizer(wx.VERTICAL)
        scrollPanelSizer.Add(self.__imageControl)
        scrollPanel.SetSizer(scrollPanelSizer)

        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(scrollPanel, -1, wx.EXPAND)
        panel.SetSizer(panelSizer)

        self.__panelSizer = panelSizer
        self.__panel = panel
        self.__scrollPanelSizer = scrollPanelSizer
        self.__scrollPanel = scrollPanel

    def __CreateMenuBar(self) -> None:
        """ Creates the main menu.
        """

        menuFile = wx.Menu()
        itemOpenMapFile = menuFile.Append(-1, "Open map file")
        menuFile.AppendSeparator()
        itemExit = menuFile.Append(-1, "Exit")

        menuView = wx.Menu()
        self.__itemViewBottomLayer = menuView.AppendCheckItem(-1, "View bottom layer")
        self.__itemViewBottomLayer.Check(True)
        self.__itemViewTopLayer = menuView.AppendCheckItem(-1, "View top layer")
        self.__itemViewTopLayer.Check(True)
        self.__itemViewAttributes = menuView.AppendCheckItem(-1, "View attributes")
        self.__itemViewAttributes.Check(True)
        self.__itemViewEntities = menuView.AppendCheckItem(-1, "View entities")
        self.__itemViewEntities.Check(True)

        menuExport = wx.Menu()
        itemExportMap = menuExport.Append(-1, "Export map to JSON + PNG")

        menu = wx.MenuBar()
        menu.Append(menuFile, "File")
        menu.Append(menuView, "View")
        menu.Append(menuExport, "Export")
        self.SetMenuBar(menu)

        self.Bind(wx.EVT_MENU, self.OnOpenMapFile,  itemOpenMapFile)
        self.Bind(wx.EVT_MENU, self.OnExit,  itemExit)

        self.Bind(wx.EVT_MENU, self.OnVisibleLayerChanged, self.__itemViewBottomLayer)
        self.Bind(wx.EVT_MENU, self.OnVisibleLayerChanged, self.__itemViewTopLayer)
        self.Bind(wx.EVT_MENU, self.OnVisibleLayerChanged, self.__itemViewAttributes)
        self.Bind(wx.EVT_MENU, self.OnVisibleLayerChanged, self.__itemViewEntities)

        self.Bind(wx.EVT_MENU, self.OnExportMap, itemExportMap)

    def OnOpenMapFile(self, event):
        """ Loads a map file.
        """

        with wx.FileDialog(self, "Open Map file", wildcard="Multiplayer Map (*.lpm)|*.lpm|Singleplayer Map (*.lps)|*.lps",
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

        threading.Thread(target=self.LoadAndShowMapFile, args=(fileDialog.GetPath(),)).start()

    def OnExit(self, event):
        """ Closes the application
        """
        self.Close(True)

    def OnVisibleLayerChanged(self, event):
        """ Updates the view.
        """
        self.__UpdateViewLayersAndAttributes()

    def OnExportMap(self, event):
        """ Exports the map data to JSON + PNG.
        """
        baseFileName = str(Path(self.__mapFileName).with_suffix(""))
        self.ExportMap(baseFileName)

        dlg = wx.MessageDialog(None, f"Map exported to {baseFileName}.json", "Export finished", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def ShowError(self, err : str) -> None:
        """ Shows an error message.

        Args:
            err (Exception): The error message.
        """
        dlg = wx.MessageDialog(None, err, "An error occurred ...", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def LoadAndShowMapFile(self, mapFileName : str) -> None:
        """ Loads the map file and shows it.

        Args:
            mapFileName (str): The filename of the map.
        """
        try:
            with wx.BusyInfo("Please wait, loading ...", self):
                maps = mapd.ReadMaps(mapFileName)
                map = maps[0]
                cplcFile = cplc.ReadCplcFile(mapFileName, self.__creatureLibrary)

                self.BitmapBottom = FrameMain.RenderBitmapFromLayer(map, 0)
                self.BitmapTop = FrameMain.RenderBitmapFromLayer(map, 1)
                self.BitmapAttributes = FrameMain.RenderBitmapFromTerrainAttributes(map, self.__terrainAttributeIconList)
                self.BitmapEntities = FrameMain.RenderBitmapFromEntities(map, cplcFile)

                self.__UpdateViewLayersAndAttributes()

                self.__mapFileName = mapFileName
                self.__map = map
                self.__cplcFile = cplcFile

        except Exception as err:
            self.ShowError(str(err))

    @staticmethod
    def RenderBitmapFromLayer(map : mapd.MapdFile, layerIndex : int) -> wx.Bitmap:
        """ Renders a bitmap from a layer.
            (This works only on little endian architecture because of numpy Uint32 ABGR values.)

        Args:
            map (mapd.MapdFile): The map with the layers.
            layerIndex (int): The index of the layer to render.

        Returns:
            wx.Bitmap: The rendered bitmap.
        """
        layer = map.LayerList[layerIndex]
        imageData = map.RenderLayerUint32Abgr(layerIndex)
        data = imageData.transpose().tobytes()

        bitmap = wx.Bitmap.FromBufferRGBA(layer.MapWidthInPixels, layer.MapHeightInPixels, data)
        return bitmap

    @staticmethod
    def RenderBitmapFromTerrainAttributes(map : mapd.MapdFile, terrainAttributeIcons : list[wx.Bitmap]) -> wx.Bitmap:
        """ Renders the tile attributes view in a bitmap.

        Args:
            map (mapd.MapdFile): The map with the layers and tile attributes.
            terrainAttributeIcons (list[wx.Bitmap]): The tile attribute icons.

        Returns:
            wx.Bitmap: The attribute bitmap for the whole map.
        """

        layerBottom = map.LayerList[0]
        tileWidth = layerBottom.TileWidthInPixels
        tileHeight = layerBottom.TileHeightInPixels

        bmp = wx.Bitmap(layerBottom.MapWidthInPixels, layerBottom.MapHeightInPixels, 32)

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(wx.WHITE, wx.BRUSHSTYLE_TRANSPARENT))
        dc.Clear()

        for tileRow in range(layerBottom.MapHeightInTiles):
           for tileColumn in range(layerBottom.MapWidthInTiles):
               attribute = layerBottom.TerrainAttributes.GetTerrainAttribute(tileColumn, tileRow)

               if attribute != ta.ETerrainAttribute.OPEN:
                   attributeIcon = terrainAttributeIcons[attribute]
                   dc.DrawBitmap(attributeIcon, tileColumn * tileWidth, tileRow * tileHeight)

        dc.SelectObject(wx.NullBitmap)
        return bmp

    @staticmethod
    def RenderBitmapFromEntities(map : mapd.MapdFile, cplcFile : cplc.CplcFile) -> wx.Bitmap:
        """ Renders the tile attributes view in a bitmap.

        Args:
            map (mapd.MapdFile): The map with the layers and tile attributes.
            cplcFile (cplc.CplcFile): The CPLC file with the entities.

        Returns:
            wx.Bitmap: The attribute bitmap for the whole map.
        """

        layerBottom = map.LayerList[0]

        bmp = wx.Bitmap(layerBottom.MapWidthInPixels, layerBottom.MapHeightInPixels, 32)

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(wx.WHITE, wx.BRUSHSTYLE_TRANSPARENT))
        dc.Clear()

        for entity in cplcFile.EntityList:
            if entity.Image is None:
                r = 10
                x = entity.X - r
                y = entity.Y - r
                dc.DrawCircle(x, y, r)
            else:
                entityBmp = wx.Bitmap(entity.Image)
                x = entity.X - entity.Image.Width // 2
                y = entity.Y - entity.Image.Height // 2
            
                dc.DrawBitmap(entityBmp, x, y)

        dc.SelectObject(wx.NullBitmap)
        return bmp

    def __RenderLayerView(self, bottomLayerVisible : bool, topLayerVisible : bool, attributesVisible : bool,
                          entitiesVisible : bool, transparentBackground : bool) -> wx.Bitmap:
        """ Renders layer and attributes view.

        Args:
            bottomLayerVisible (bool): True if bottom layer shall be visible.
            topLayerVisible (bool): True if top layer shall be visible.
            attributesVisible (bool): True if attributes shall be visible.

        Returns:
            wx.Bitmap: The resulting bitmap.
        """
        bmp = wx.Bitmap(self.BitmapBottom.GetWidth(), self.BitmapBottom.GetHeight(), 32)

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)

        backgroundBrushStyle = wx.BRUSHSTYLE_TRANSPARENT if transparentBackground else wx.BRUSHSTYLE_SOLID
        dc.SetBackground(wx.Brush(wx.WHITE, backgroundBrushStyle))

        dc.Clear()

        if bottomLayerVisible:
            dc.DrawBitmap(self.BitmapBottom, 0, 0)

        if topLayerVisible:
            dc.DrawBitmap(self.BitmapTop, 0, 0)

        if attributesVisible:
            dc.DrawBitmap(self.BitmapAttributes, 0, 0)

        if entitiesVisible:
            dc.DrawBitmap(self.BitmapEntities, 0, 0)

        dc.SelectObject(wx.NullBitmap)

        return bmp

    def __UpdateViewLayersAndAttributes(self) -> None:
        """ Updates the layer view.
        """
        bmp = self.__RenderLayerView(self.__itemViewBottomLayer.IsChecked(),
                                     self.__itemViewTopLayer.IsChecked(),
                                     self.__itemViewAttributes.IsChecked(),
                                     self.__itemViewEntities.IsChecked(),
                                     False)

        self.__imageControl.SetBitmap(bmp)

        self.__panel.Layout()
        self.__panelSizer.Layout()
        self.__scrollPanel.Layout()
        self.__scrollPanelSizer.Layout()
        self.__imageControl.Layout()

    def ExportMap(self, baseFileName : str) -> None:
        """ Exports the currently loaded map for use in other programs.
            Creates 3 files:

                map_bottom.png   -> the bottem layer
                map_top.png      -> the top layer
                map.json         -> map informations

        Args:
            baseFileName (str): The base filename for the 3 created files.
        """

        # export bottom layer as PNG
        fileNameBottomLayer = baseFileName + "_bottom.png"
        bmpBottom = self.__RenderLayerView(True, False, False, False, True)
        bmpBottom.SaveFile(fileNameBottomLayer, wx.BITMAP_TYPE_PNG)

        # export top layer as PNG
        fileNameTopLayer = baseFileName + "_top.png"
        bmpTop = self.__RenderLayerView(False, True, False, False, True)
        bmpTop.SaveFile(fileNameTopLayer, wx.BITMAP_TYPE_PNG)

        layer = self.__map.LayerList[0]

        # create tile terrain attribute map
        attributeMapRows = []
        for tileRow in range(layer.MapHeightInTiles):
            row = []
            for tileColumn in range(layer.MapHeightInTiles):
                row.append(int(layer.TerrainAttributes.GetTerrainAttribute(tileColumn, tileRow)))
            attributeMapRows.append(pjson.JsonFlatList(row))

        # create entity list
        cplcFile = self.__cplcFile
        entityList = []

        for entity in cplcFile.EntityList:
            entityJson = {
                "Id" : entity.Id,
                "IsOptional" : entity.IsOptional,
                "Name" : entity.Name,
                "X" : entity.X,
                "Y" : entity.Y
            }
            entityList.append(entityJson)

        # create map informations
        info = {
            "BottomLayer" : str(Path(fileNameBottomLayer).name),
            "TopLayer" : str(Path(fileNameTopLayer).name),
            "TileWidthInPixels" : layer.TileWidthInPixels,
            "TileHeightInPixels" : layer.TileHeightInPixels,
            "MapWidthInTiles" : layer.MapWidthInTiles,
            "MapHeightInTiles" : layer.MapHeightInTiles,
            "MapWidthInPixels" : layer.MapWidthInPixels,
            "MapHeightInPixels" : layer.MapHeightInPixels,

            "TerrainAttributes" : { attr.name: attr.value for attr in ta.ETerrainAttribute },
            "TerrainAttributeMapRows" : attributeMapRows,

            "EntityList" : entityList
        }

        # write JSON file
        fileNameJson = baseFileName + ".json"
        pjson.ExportAsJsonFile(fileNameJson, info)

if __name__ == "__main__":

    app = wx.App()

    frm = FrameMain()
    frm.Show()

    app.MainLoop()


