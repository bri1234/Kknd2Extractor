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

import Kknd2Reader.KkndFileMapd as mapd
import Kknd2Reader.TerrainAttributes as ta

class FrameMain(wx.Frame):
    """ The main window.
    """
    
    def __init__(self):
        super().__init__(None, wx.ID_ANY, "KKND2 Map Viewer", size = (1000, 800)) 

        terrainIconsPath = os.path.join("Kknd2Reader", "TerrainAttributeIcons.png")
        self.__terrainAttributeIconList = FrameMain.__LoadTerrainAttributeIcons(terrainIconsPath)

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

    def __CreateWidgets(self) -> None:
        """ Creates the GUI.
        """
        panel = wx.Panel(self, wx.ID_ANY)

        scrollPanel = wxls.ScrolledPanel(panel, -1, style = wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        scrollPanel.SetAutoLayout(1)
        scrollPanel.SetupScrolling()

        self.__ImageControl = wx.StaticBitmap(scrollPanel, wx.ID_ANY)

        scrollPanelSizer = wx.BoxSizer(wx.VERTICAL)
        scrollPanelSizer.Add(self.__ImageControl)
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
        pass

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

                self.BitmapBottom = FrameMain.RenderBitmapFromLayer(map, 0)
                self.BitmapTop = FrameMain.RenderBitmapFromLayer(map, 1)
                self.BitmapAttributes = FrameMain.RenderBitmapFromTerrainAttributes(map, self.__terrainAttributeIconList)

                self.__UpdateViewLayersAndAttributes()

        except Exception as err:
            self.ShowError(str(err))

    @staticmethod
    def RenderBitmapFromLayer(map : mapd.MapdFile, layerIndex : int) -> wx.Bitmap:
        """ Renders a bitmap from a layer.

        Args:
            map (mapd.MapdFile): The map with the layers.
            layerIndex (int): The index of the layer to render.

        Returns:
            wx.Bitmap: The rendered bitmap.
        """
        layer = map.LayerList[layerIndex]
        imageData = map.RenderLayer(layerIndex)
        data = bytearray()

        for row in range(layer.MapHeightInPixels):
            for column in range(layer.MapWidthInPixels):
                rgb = imageData[column, row]

                data.append((rgb >> 16) % 0xFF)     # red
                data.append((rgb >> 8) & 0xFF)      # green
                data.append(rgb & 0xFF)             # blue

                data.append(0xFF)                   # alpha

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

    def __UpdateViewLayersAndAttributes(self) -> None:
        """ Updates the layer view.
        """
        bmp = wx.Bitmap(self.BitmapBottom.GetWidth(), self.BitmapBottom.GetHeight(), 32)

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.Clear()

        if self.__itemViewBottomLayer.IsChecked():
            dc.DrawBitmap(self.BitmapBottom, 0, 0)

        if self.__itemViewTopLayer.IsChecked():
            dc.DrawBitmap(self.BitmapTop, 0, 0)

        if self.__itemViewAttributes.IsChecked():
            dc.DrawBitmap(self.BitmapAttributes, 0, 0)

        dc.SelectObject(wx.NullBitmap)

        self.__ImageControl.SetBitmap(bmp)
        
        self.__panel.Layout()
        self.__panelSizer.Layout()
        self.__scrollPanel.Layout()
        self.__scrollPanelSizer.Layout()
        self.__ImageControl.Layout()


if __name__ == "__main__":

    app = wx.App()

    frm = FrameMain()
    frm.Show() 
    
    app.MainLoop() 


