# -*- coding: utf-8 -*-

import tkinter as tk
from typing import Any
import KkndFileCompression as compression
import KkndFileContainer as container
import KkndFileMobd as kkndMobd

FileList : list[container.ContainerFile]
PhotoImg : tk.PhotoImage
ListboxFiles : tk.Listbox

def SetPixel(img : tk.PhotoImage, x : int, y : int, colorRgb : int) -> None:
    img.put( f"#{colorRgb & 0xFFFFFF:06X}", ( x, y ) )

def CalculateImageWidthAndHeight(mobdFile : kkndMobd.MobdFile) -> tuple[int, int]:
    width = 0
    height = 0

    for animation in mobdFile.AnimationList:
        maxWidth, maxHeight = animation.GetMaxWidthAndHeight()

        width = max(width, maxWidth * len(animation.FrameList))
        height += maxHeight

    return width, height

def CreateFileAnimationsImage(photoImg : tk.PhotoImage, mobdFile : kkndMobd.MobdFile) -> None:

    photoImg.blank()

    offY = 0
    idx = 0
    for animation in mobdFile.AnimationList:
        idx += 1
        print(f"Draw animation {idx}/{len(mobdFile.AnimationList)}")

        offX = 0
        imgHeight = 0
        for frame in animation.FrameList:
            palette = frame.Palette
            img = frame.Image

            for x in range(img.Width):
                for y in range(img.Height):
                    pixel = img.GetPixel(x, y)
                    if pixel >= 0 and pixel < len(palette.Colors):
                        color = palette.Colors[pixel]
                        SetPixel(photoImg, x + offX, y + offY, color)

            offX += img.Width
            imgHeight = max(imgHeight, img.Height)

        offY += imgHeight

def ListBoxFileSelected(event : Any) -> None:
    global FileList, PhotoImg
    
    selection : int = event.widget.curselection()[0]
    file = FileList[selection]

    mobdFile = kkndMobd.MobdFile()
    mobdFile.ReadAnimations(file.RawData, file.FileOffset)

    CreateFileAnimationsImage(PhotoImg, mobdFile)

def BuildGui(window : tk.Tk) -> tuple[tk.PhotoImage, tk.Listbox]:
    WIDTH = 5000
    HEIGHT = 5000

    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.columnconfigure(2, weight=1000)
    window.columnconfigure(3, weight=1)
    window.rowconfigure(0, weight=1000)
    window.rowconfigure(1, weight=1)

    sbListboxV = tk.Scrollbar(window,orient="vertical")
    sbListboxV.grid(column=0, row=0, sticky="NS")

    listboxFiles = tk.Listbox(window, yscrollcommand = sbListboxV.set)
    listboxFiles.grid(column=1, row=0, sticky="NSWE")
    listboxFiles.bind("<<ListboxSelect>>", ListBoxFileSelected)

    sbListboxV.config(command = listboxFiles.yview) # type: ignore

    sbCanvasV = tk.Scrollbar(window,orient="vertical")
    sbCanvasV.grid(column=3, row=0, sticky="NS")

    sbCanvasH = tk.Scrollbar(window,orient="horizontal")
    sbCanvasH.grid(column=2, row=1, sticky="WE")

    canvas = tk.Canvas(window, bg="black", xscrollcommand=sbCanvasH.set, yscrollcommand=sbCanvasV.set, scrollregion=(0,0,WIDTH,HEIGHT))
    
    photoImg = tk.PhotoImage(width=WIDTH, height=HEIGHT)
    canvas.create_image((photoImg.width() / 2, photoImg.height() / 2), image=photoImg, state="normal") # type: ignore
    
    canvas.grid(column=2, row=0, sticky="NSWE")

    sbCanvasV.config(command=canvas.yview) # type: ignore
    sbCanvasH.config(command=canvas.xview) # type: ignore

    return photoImg, listboxFiles

def Main() -> None:
    global FileList, PhotoImg, ListboxFiles

    containerData, _, _ = compression.UncompressFile("assets/spritesheets/gamesprt.lpk")
    fileTypeList, _ = container.ReadFileTypeList(containerData)

    if len(fileTypeList) != 1 or fileTypeList[0].FileType != "MOBD":
        raise Exception("Unexpected file type")

    FileList = fileTypeList[0].FileList
    
    window = tk.Tk()
    PhotoImg, ListboxFiles = BuildGui(window)
    
    for file in FileList:
        ListboxFiles.insert(tk.END, file.FileName)
    
    tk.mainloop()

if __name__ == "__main__":
    
    Main()

