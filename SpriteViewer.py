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
from Kknd2Reader.KkndFileMobd import MobdFile, SaveMobdFileStructureInfo, MobdColorPalette

from pathlib import Path
from termcolor import cprint

def Rgb(rgb : int) -> tuple[int, int, int]:
    return (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, (rgb >> 0) & 0xFF

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

        # create menu
        menuFile = wx.Menu()
        menuFile.AppendSeparator()
        itemFileExit = menuFile.Append(-1, "Exit")

        menuMisc = wx.Menu()
        itemMiscExportImageList = menuMisc.Append(-1, "Export image list")
        itemMiscExportMobdFileStructure = menuMisc.Append(-1, "Export Mobd file structure")
        itemMiscPrintPalette = menuMisc.Append(-1, "Print palette")
        itemMiscTest = menuMisc.Append(-1, "Test")

        menu = wx.MenuBar()
        menu.Append(menuFile, "File")
        menu.Append(menuMisc, "Misc")
        self.SetMenuBar(menu)

        # create menu bindings
        self.Bind(wx.EVT_MENU, self.OnExit,  itemFileExit)

        self.Bind(wx.EVT_MENU, self.OnMiscExportImageList, itemMiscExportImageList)
        self.Bind(wx.EVT_MENU, self.OnMiscExportMobdFileStructure, itemMiscExportMobdFileStructure)
        self.Bind(wx.EVT_MENU, self.OnMiscPrintPalette, itemMiscPrintPalette)
        self.Bind(wx.EVT_MENU, self.OnMiscTest, itemMiscTest)

    def OnExit(self, event) -> None:
        """ Closes the application
        """
        self.Close(True)

    def OnMiscExportImageList(self, event) -> None:
        """ Exports the units data to JSON + PNG.
        """
        idx = int(self.__listBox.Selection)

        mobdFile = MobdFile(self.__mobdFileList[idx])
        FrameMain.__UpdateBitmap(mobdFile)

        animationIdx = 0
        for animation in mobdFile.AnimationList:
            frameIdx = 0
            for frame in animation.FrameList:
                bmp = frame.Bitmap
                bmp.SaveFile(f"export image{idx}_{animationIdx}_{frameIdx}.png", wx.BITMAP_TYPE_PNG)
                frameIdx += 1

            animationIdx += 1

    def OnMiscExportMobdFileStructure(self, event) -> None:
        """ Exports the Mobd file structure.
        """
        SaveMobdFileStructureInfo("mobd file structure info.txt")

    def OnMiscPrintPalette(self, event) -> None:
        """ Prints the palette of the selected animation.
        """
        idx = int(self.__listBox.Selection)

        mobdFile = MobdFile(self.__mobdFileList[idx])

        for paletteIdx in MobdColorPalette.MobdColorPalettes:
            palette : MobdColorPalette = MobdColorPalette.MobdColorPalettes[paletteIdx]
            print(f"***** Palette @ {palette.PalettePosition} ")
            colors = palette.ColorsRgb
            for idx in range(len(colors)):
                color = colors[idx]
                cprint(f"{idx:03}\t{color:06X}", on_color=Rgb(color))

    def OnMiscTest(self, event) -> None:
        """ For testing purposes.
        """
        print("TEST")

        mobdFileIdx = 0
        for mobdFileData in self.__mobdFileList:
            mobdFile = MobdFile(mobdFileData)
            for animation in mobdFile.AnimationList:
                for frame in animation.FrameList:
                    palette = frame.ColorPalette
                    if len(palette.ColorsRgb) == 256:
                        
                        count = 0
                        for idx in range(256):
                            if palette.ColorsRgb[idx] == MobdColorPalette.ColorsSeries9BuildingsRgbBlu[idx]:
                                count += 1

                        print(f"file {mobdFileIdx} animation {frame.AnimationIndex} frame {frame.FrameIndex} Count: {count}")

            mobdFileIdx += 1

        print("DONE")

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
    def __LoadSprites() -> list[ContainerFile]:
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


