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

from Kknd2Reader.KkndFileCompression import UncompressFile
from Kknd2Reader.KkndFileContainer import ReadFileTypeList, ContainerFile
from Kknd2Reader.KkndFileMobd import MobdFile, MobdFrame

from pathlib import Path

class FrameMain(wx.Frame):
    """ The main window.
    """
    __mobdFileList : list[ContainerFile]

    def __init__(self):
        super().__init__(None, title = "KKND2 Sprite Viewer", size = (1000, 800))

        self.__mobdFileList = FrameMain.__LoadSprites()

        self.__CreateMenuBar()
        self.__CreateWidgets()

        self.__UpdateSpriteFilesListBox()

    def __CreateWidgets(self) -> None:
        """ Creates the GUI.
        """
        splitter = wx.SplitterWindow(self)

        self.__listBox = wx.ListBox(splitter)
        self.__listBox.Bind(wx.EVT_LISTBOX, self.OnSpriteSelected)

        scrollPanel = wxls.ScrolledPanel(splitter, -1, style = wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        scrollPanel.SetAutoLayout(1)
        scrollPanel.SetupScrolling()

        self.__imageControl = wx.StaticBitmap(scrollPanel)

        scrollPanelSizer = wx.BoxSizer(wx.VERTICAL)
        scrollPanelSizer.Add(self.__imageControl)
        scrollPanel.SetSizer(scrollPanelSizer)

        splitter.SplitVertically(self.__listBox, scrollPanel)
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

        menuMisc = wx.Menu()
        itemExport = menuMisc.Append(-1, "Export image")
        itemCreatePalette = menuMisc.Append(-1, "Create palette")

        menu = wx.MenuBar()
        menu.Append(menuFile, "File")
        menu.Append(menuMisc, "Misc")
        self.SetMenuBar(menu)

        self.Bind(wx.EVT_MENU, self.OnExit,  itemExit)

        self.Bind(wx.EVT_MENU, self.OnExport, itemExport)
        self.Bind(wx.EVT_MENU, self.OnCreatePalette, itemCreatePalette)

    def OnExit(self, event) -> None:
        """ Closes the application
        """
        self.Close(True)

    def OnExport(self, event) -> None:
        """ Exports the units data to JSON + PNG.
        """
        idx = int(self.__listBox.Selection)

        mobdFile = MobdFile(self.__mobdFileList[idx])
        FrameMain.__UpdateBitmap(mobdFile)

        bmp = mobdFile.AnimationList[4].FrameList[0].Bitmap
        bmp.SaveFile(f"image{idx}.png", wx.BITMAP_TYPE_PNG)

    @staticmethod
    def ConvertColorsToPalette(colorIndexColors : dict[int, int]) -> list[int]:
        palette : list[int] = [0] * 256

        for k in colorIndexColors:
            palette[k] = colorIndexColors[k]

        return palette
    
    @staticmethod
    def CreateColorPalette(referenceFile : str, mobdFrame : MobdFrame) -> dict[int, int]:

        width = mobdFrame.Image.Width
        height = mobdFrame.Image.Height

        img = wx.Image()
        with open(referenceFile, "rb") as file:
            img.LoadFile(file)

        if img.GetWidth() != width or img.GetHeight() != height:
            raise Exception("invalid img size")
        
        colorIndexColors : dict[int, int] = {}
        colorIndexList : dict[int, bool] = {}

        for column in range(width):
            for row in range(height):
                colorIndex = mobdFrame.Image.GetPixel(column, row)
                if colorIndex == 0:
                    continue
                
                colorIndexList[colorIndex] = True

                a = img.GetAlpha(column, row)
                if a == 0:
                    continue

                c = (img.GetRed(column, row) << 16) | (img.GetGreen(column, row) << 8) | img.GetBlue(column, row)

                if colorIndex in colorIndexColors:
                    if c != colorIndexColors[colorIndex]:
                        raise Exception(f"different color for color index {colorIndex} at {column},{row}: old 0x{colorIndexColors[colorIndex]:08X} new 0x{c:08X}")
                else:
                    colorIndexColors[colorIndex] = c
        
        for colorIndex in colorIndexList.keys():
            if colorIndex not in colorIndexColors:
                raise Exception(f"missing color for color index {colorIndex}")

        return colorIndexColors
    
    @staticmethod
    def MergeColors(colors1 : dict[int, int], colors2 : dict[int, int]) -> dict[int, int]:

        colors = colors1.copy()

        for colorIndex in colors2:
            c = colors2[colorIndex]

            if colorIndex in colors:
                if c != colors[colorIndex]:
                    raise Exception(f"different color for color index {colorIndex}: old 0x{colors[colorIndex]:08X} new 0x{c:08X}")
            else:
                colors[colorIndex] = c

        return colors

    def OnCreatePalette(self, event) -> None:
        mobdFile = MobdFile(self.__mobdFileList[108])
        frame108 = mobdFile.AnimationList[5].FrameList[0]

        mobdFile = MobdFile(self.__mobdFileList[102])
        frame102 = mobdFile.AnimationList[4].FrameList[0]

        colorsRed108 = FrameMain.CreateColorPalette("image108 colors red.png", frame108)
        colorsRed102 = FrameMain.CreateColorPalette("image102 colors red.png", frame102)
        colorsRed = FrameMain.MergeColors(colorsRed108, colorsRed102)
        paletteRed = FrameMain.ConvertColorsToPalette(colorsRed)
        FrameMain.PrintPalette(paletteRed)

        colorsGreen108 = FrameMain.CreateColorPalette("image108 colors green.png", frame108)
        colorsGreen102 = FrameMain.CreateColorPalette("image102 colors green.png", frame102)
        colorsGreen = FrameMain.MergeColors(colorsGreen108, colorsGreen102)
        paletteGreen = FrameMain.ConvertColorsToPalette(colorsGreen)
        FrameMain.PrintPalette(paletteGreen)

        colorsBlue108 = FrameMain.CreateColorPalette("image108 colors blue.png", frame108)
        colorsBlue102 = FrameMain.CreateColorPalette("image102 colors blue.png", frame102)
        colorsBlue = FrameMain.MergeColors(colorsBlue108, colorsBlue102)
        paletteBlue = FrameMain.ConvertColorsToPalette(colorsBlue)
        FrameMain.PrintPalette(paletteBlue)

        FrameMain.DiffPalette(paletteRed, paletteGreen, paletteBlue)

    @staticmethod
    def PrintPalette(palette : list[int]) -> None:
        print(",".join([f"0x{c:08X}" for c in palette]))
        print()

    @staticmethod
    def DiffPalette(paletteRed : list[int], paletteGreen : list[int], paletteBlue : list[int]) -> None:
        for idx in range(256):
            r = paletteRed[idx]
            g = paletteGreen[idx]
            b = paletteBlue[idx]
            if r == g and r == b:
                continue

            if r != g and r != b and g != b:
                print(f"diff 3: {idx:3d} 0x{r:08X} 0x{g:08X} 0x{b:08X}")
                continue

            print(f"diff 2: {idx}")


    def OnSpriteSelected(self, event) -> None:
        """ User has selected a new sprite.

        Args:
            event: The new selected sprite.
        """
        idx = int(event.Selection)

        # with open(f"test{idx}.bin", "wb") as file:
        #     file.write(self.__mobdFileList[idx].RawData)

        mobdFile = MobdFile(self.__mobdFileList[idx])
        FrameMain.__UpdateBitmap(mobdFile)

        bmp = FrameMain.__CreateFileAnimationsImage(mobdFile)
        self.__imageControl.SetBitmap(bmp)

    @staticmethod
    def __UpdateBitmap(mobdFile : MobdFile) -> None:
        for animation in mobdFile.AnimationList:
            for frame in animation.FrameList:
                if frame.Bitmap is not None:
                    continue
                
                pixelData = frame.RenderFrameUInt32Abgr().transpose().tobytes()
                frame.Bitmap = wx.Bitmap.FromBufferRGBA(frame.Image.Width, frame.Image.Height, pixelData)

    @staticmethod
    def __CalculateCanvasSize(mobdFile : MobdFile) -> tuple[int, int]:
        """ Calculates the size of the canvas to show all sprite animations.

        Args:
            mobdFile (MobdFile): The sprite.

        Returns:
            tuple[int, int]: The width and the height of the canvas to draw the animations.
        """
        canvasWidth = 0
        canvasHeight = 0

        for animation in mobdFile.AnimationList:

            maxFrameWidth, maxFrameHeight = animation.GetMaxWidthAndHeight()

            canvasWidth = max(canvasWidth, maxFrameWidth * len(animation.FrameList))
            canvasHeight += maxFrameHeight

        return canvasWidth, canvasHeight
    
    @staticmethod
    def __CreateFileAnimationsImage(mobdFile : MobdFile) -> wx.Bitmap:
        """ Draws all animations of a sprite to a bitmap.

        Args:
            mobdFile (MobdFile): The sprite to be drawn.

        Returns:
            wx.Bitmap: The bitmap with all sprite animations. 
        """
        canvasWidth, canvasHeight = FrameMain.__CalculateCanvasSize(mobdFile)
        bmp = wx.Bitmap(canvasWidth, canvasHeight, 32)

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(wx.WHITE, wx.BRUSHSTYLE_TRANSPARENT))
        dc.Clear()

        offsetY = 0
        for animation in mobdFile.AnimationList:
            maxFrameWidth, maxFrameHeight = animation.GetMaxWidthAndHeight()

            offsetX = 0
            for frame in animation.FrameList:
                dc.DrawBitmap(frame.Bitmap, offsetX, offsetY)

                offsetX += maxFrameWidth

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

    def __UpdateSpriteFilesListBox(self) -> None:
        """ Shows all loaded sprites in the sprite ListBox.
        """
        for file in self.__mobdFileList:
            self.__listBox.Append(f"{file.FileNumber}: {file.FileName}")

    @staticmethod
    def __LoadSprites() -> list[MobdFile]:
        """ Load the sprites.

        Returns:
            list[MobdFile]: List of all sprites.
        """
        containerData, _, _ = UncompressFile("assets/spritesheets/gamesprt.lpk")
        fileTypeList, _ = ReadFileTypeList(containerData, "Kknd2Reader/gamesprt.lpk.json")

        if len(fileTypeList) != 1 or fileTypeList[0].FileType != "MOBD":
            raise Exception("Unexpected file type")

        return fileTypeList[0].FileList
    


if __name__ == "__main__":

    app = wx.App()

    frm = FrameMain()
    frm.Show()

    app.MainLoop()

# 7: 256, okay
# 104: not okay

