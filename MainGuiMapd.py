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
import threading

import KkndFileMapd as mapd


class FrameMain(wx.Frame):
    """ The main window.
    """
    
    Map : mapd.MapdFile

    def __init__(self):
        super().__init__(None, wx.ID_ANY, "KKND2 Map Viewer", size = (1000, 800)) 

        self.Map = mapd.MapdFile()

        self.__CreateMenuBar()
        self.__CreateWidgets()

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
        # panelSizer.AddSpacer(50)
        panelSizer.Add(scrollPanel, -1, wx.EXPAND)
        panel.SetSizer(panelSizer)

    def __CreateMenuBar(self) -> None:
        """ Creates the main menu.
        """

        menuFile = wx.Menu()
        itemOpenMapFile = menuFile.Append(-1, "Open map file")
        menuFile.AppendSeparator()
        itemExit = menuFile.Append(-1, "Exit")

        menu = wx.MenuBar()
        menu.Append(menuFile, "File")
        self.SetMenuBar(menu)

        self.Bind(wx.EVT_MENU, self.OnOpenMapFile,  itemOpenMapFile)
        self.Bind(wx.EVT_MENU, self.OnExit,  itemExit)

    def OnOpenMapFile(self, event):
        """ Loads a map file.
        """

        with wx.FileDialog(self, "Open Map file", wildcard="Multiplayer Map (*.lpm)|*.lpm|Singleplayer Map (*.lps)|*.lps",
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
        threading.Thread(target=self.LoadAndShowMapFile, args=(fileDialog.GetPath(),)).start()

    def ShowError(self, err : str) -> None:
        """ Shows an error message.

        Args:
            err (Exception): The error message.
        """
        dlg = wx.MessageDialog(None, err, "An error occurred ...", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        """ Closes the application
        """
        self.Close(True)

    def LoadAndShowMapFile(self, mapFileName : str) -> None:
        """ Loads the map file and shows it.

        Args:
            mapFileName (str): The filename of the map.
        """
        try:
            with wx.BusyInfo("Please wait, loading ...", self):
                maps = mapd.ReadMaps(mapFileName)
                self.Map = maps[0]
                self.ShowMapFile(self.Map)

        except Exception as err:
            self.ShowError(str(err))

    def ShowMapFile(self, map : mapd.MapdFile) -> None:
        """ Draws the bottom layer.

        Args:
            map (mapd.MapdFile): The map file.
        """
        layerIndex = 0

        layer = map.LayerList[layerIndex]
        imageData = map.RenderLayer(layerIndex)
        data = bytearray()

        for row in range(layer.MapHeightInPixels):
            for column in range(layer.MapWidthInPixels):
                rgb = imageData[column, row]

                data.append((rgb >> 16) % 0xFF)
                data.append((rgb >> 8) & 0xFF)
                data.append(rgb & 0xFF)

        bmp = wx.Bitmap.FromBuffer(layer.MapWidthInPixels, layer.MapHeightInPixels, data)
        self.__ImageControl.SetBitmap(bmp)

if __name__ == "__main__":

    app = wx.App()

    frm = FrameMain()
    frm.Show() 
    
    app.MainLoop() 


