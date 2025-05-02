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

from Kknd2Reader.KkndFileCompression import UncompressFile
from Kknd2Reader.KkndFileContainer import ReadFileTypeList
from Kknd2Reader.KkndFileMobd import MobdFile

from pathlib import Path

class FrameMain(wx.Frame):
    """ The main window.
    """

    def __init__(self):
        super().__init__(None, title = "KKND2 Sprite Viewer", size = (1000, 800))

        self.__CreateMenuBar()
        self.__CreateWidgets()
        self.__LoadSprites()

    def __CreateWidgets(self) -> None:
        """ Creates the GUI.
        """
        splitter = wx.SplitterWindow(self)

        self.__listBox = wx.ListBox(splitter)
        self.__listBox.Bind(wx.EVT_LISTBOX, self.OnSpriteSelected)

        self.__imageControl = wx.StaticBitmap(splitter)

        splitter.SplitVertically(self.__listBox, self.__imageControl)
        splitter.SetMinimumPaneSize(250)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def __CreateMenuBar(self) -> None:
        """ Creates the main menu.
        """

        menuFile = wx.Menu()
        menuFile.AppendSeparator()
        itemExit = menuFile.Append(-1, "Exit")

        menuExport = wx.Menu()
        itemExport = menuExport.Append(-1, "Export to JSON")

        menu = wx.MenuBar()
        menu.Append(menuFile, "File")
        menu.Append(menuExport, "Export")
        self.SetMenuBar(menu)

        self.Bind(wx.EVT_MENU, self.OnExit,  itemExit)

        self.Bind(wx.EVT_MENU, self.OnExport, itemExport)

    def OnExit(self, event) -> None:
        """ Closes the application
        """
        self.Close(True)

    def OnExport(self, event) -> None:
        """ Exports the units data to JSON + PNG.
        """
        baseFileName = str(Path(self.__mapFileName).with_suffix(""))
        self.ExportMap(baseFileName)

        dlg = wx.MessageDialog(None, f"Map exported to {baseFileName}.json", "Export finished", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnSpriteSelected(self, event) -> None:
        idx = int(event.Selection)
        self.__ShowMobdFile(idx)

    def __ShowMobdFile(self, fileIndex : int) -> None:
        mobdFile = MobdFile(self.__fileList[fileIndex])
        bmp = FrameMain.__CreateFileAnimationsImage(mobdFile)
        self.__imageControl.SetBitmap(bmp)

    @staticmethod
    def __CalculateImageSize(mobdFile : MobdFile) -> tuple[int, int]:
        imgWidth = 0
        imgHeight = 0

        for animation in mobdFile.AnimationList:

            maxFrameHeight = 0
            width = 0
            for frame in animation.FrameList:
                img = frame.Image
                width += img.Width
                maxFrameHeight = max(maxFrameHeight, img.Height)

            imgWidth = max(imgWidth, width)
            imgHeight += maxFrameHeight

        return imgWidth, imgHeight
    
    @staticmethod
    def __CreateFileAnimationsImage(mobdFile : MobdFile) -> wx.Bitmap:

        imgWidth, imgHeight = FrameMain.__CalculateImageSize(mobdFile)
        bmp = wx.Bitmap(imgWidth, imgHeight, 32)

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(wx.WHITE, wx.BRUSHSTYLE_TRANSPARENT))
        dc.Clear()

        offsetY = 0
        for animation in mobdFile.AnimationList:
            offsetX = 0
            maxFrameHeight = 0
            for frame in animation.FrameList:
                img = frame.Image

                dc.DrawBitmap(img.Bmp, offsetX, offsetYf)

                maxFrameHeight = max(maxFrameHeight, img.Height)
                offsetX += img.Width

            offsetY += maxFrameHeight

        dc.SelectObject(wx.NullBitmap)
        return bmp

    def ShowError(self, err : str) -> None:
        """ Shows an error message.

        Args:
            err (Exception): The error message.
        """
        dlg = wx.MessageDialog(None, err, "An error occurred ...", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def __LoadSprites(self) -> None:
        containerData, _, _ = UncompressFile("assets/spritesheets/gamesprt.lpk")
        fileTypeList, _ = ReadFileTypeList(containerData, "Kknd2Reader/gamesprt.lpk.json")

        if len(fileTypeList) != 1 or fileTypeList[0].FileType != "MOBD":
            raise Exception("Unexpected file type")

        self.__fileList = fileTypeList[0].FileList
        
        for file in self.__fileList:
            self.__listBox.Append(f"{file.FileNumber}: {file.FileName}")

if __name__ == "__main__":

    app = wx.App()

    frm = FrameMain()
    frm.Show()

    app.MainLoop()


