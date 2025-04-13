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

from typing import Any

import tkinter as tk
from tkinter import ttk
import threading

import Kknd2Reader.KkndFileCompression as compression
import Kknd2Reader.KkndFileContainer as container
import Kknd2Reader.KkndFileMobd as mobd

FileList : list[container.ContainerFile]
PhotoImg : tk.PhotoImage
ListboxFiles : tk.Listbox
Progress : tk.IntVar

def SetPixel(img : tk.PhotoImage, x : int, y : int, colorRgb : int) -> None:
    img.put( f"#{colorRgb & 0xFFFFFF:06X}", ( x, y ) )

def CalculateImageWidthAndHeight(fileList : list[container.ContainerFile]) -> tuple[int, int]:
    width = 0
    height = 0

    for file in fileList:
        print(f"File {file.FileName}")
        mobdFile = mobd.MobdFile(file)

        animationHeight = 0
        for animation in mobdFile.AnimationList:
            maxWidth, maxHeight = animation.GetMaxWidthAndHeight()

            width = max(width, maxWidth * len(animation.FrameList))
            animationHeight += maxHeight

        height = max(height, animationHeight)

    return width, height

def DrawFrame(photoImg : tk.PhotoImage, frame : mobd.MobdFrame, offX : int, offY : int) -> None:

    data = frame.RenderImageUInt32()
    dataStr : list[str] = []

    for row in range(frame.Image.Height):
        dataStr.append("{")

        for column in range(frame.Image.Width):
            dataStr.append(f"#{data[column, row]:06X}")

        dataStr.append("}")

    photoImg.put( " ".join(dataStr), ( offX, offY ) )

def CreateFileAnimationsImage(photoImg : tk.PhotoImage, mobdFile : mobd.MobdFile) -> None:
    global Progress

    Progress.set(0)
    photoImg.blank()

    offY = 0
    idx = 0
    for animation in mobdFile.AnimationList:
        idx += 1
        print(f"Draw animation {idx}/{len(mobdFile.AnimationList)}")

        offX = 0
        imgHeight = 0
        for frame in animation.FrameList:
            img = frame.Image

            DrawFrame(photoImg, frame, offX, offY)

            offX += img.Width
            imgHeight = max(imgHeight, img.Height)

        offY += imgHeight

        Progress.set(int(idx / len(mobdFile.AnimationList) * 100))

def ShowMobdFile(fileIndex : int) -> None:
    global FileList, PhotoImg, ListboxFiles

    mobdFile = mobd.MobdFile(FileList[fileIndex])

    CreateFileAnimationsImage(PhotoImg, mobdFile)

    ListboxFiles.configure(state=tk.NORMAL)

def ListBoxFileSelected(event : Any) -> None:
    selection : int = event.widget.curselection()[0]
    event.widget.configure(state=tk.DISABLED)
    threading.Thread(target=ShowMobdFile, args=(selection,)).start()

def BuildGui(window : tk.Tk, imgWidth : int, imgHeigth : int) -> tuple[tk.PhotoImage, tk.Listbox, tk.IntVar]:

    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.columnconfigure(2, weight=1000)
    window.columnconfigure(3, weight=1)
    window.rowconfigure(0, weight=1000)
    window.rowconfigure(1, weight=1)
    window.rowconfigure(2, weight=1)

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

    canvas = tk.Canvas(window, bg="black", xscrollcommand=sbCanvasH.set, yscrollcommand=sbCanvasV.set, scrollregion=(0, 0, imgWidth, imgHeigth))
    
    photoImg = tk.PhotoImage(width=imgWidth, height=imgHeigth)
    canvas.create_image((photoImg.width() / 2, photoImg.height() / 2), image=photoImg, state="normal") # type: ignore
    
    canvas.grid(column=2, row=0, sticky="NSWE")

    sbCanvasV.config(command=canvas.yview) # type: ignore
    sbCanvasH.config(command=canvas.xview) # type: ignore
    
    progressVar = tk.IntVar()
    progress = ttk.Progressbar(window, orient="horizontal", maximum=100, variable=progressVar)
    progress.grid(column=2, row=2, sticky="WE")

    return photoImg, listboxFiles, progressVar

def Main() -> None:
    global FileList, PhotoImg, ListboxFiles, Progress

    containerData, _, _ = compression.UncompressFile("assets/spritesheets/gamesprt.lpk")
    fileTypeList, _ = container.ReadFileTypeList(containerData, "gamesprt.lpk.json")

    if len(fileTypeList) != 1 or fileTypeList[0].FileType != "MOBD":
        raise Exception("Unexpected file type")

    FileList = fileTypeList[0].FileList
    
    # imgWidth, imgHeight = CalculateImageWidthAndHeight(FileList)
    imgWidth = 6500
    imgHeight = 8800

    window = tk.Tk()
    PhotoImg, ListboxFiles, Progress = BuildGui(window, imgWidth, imgHeight)
    
    for file in FileList:
        ListboxFiles.insert(tk.END, f"{file.FileNumber}: {file.FileName}")
    
    tk.mainloop()

if __name__ == "__main__":
    
    Main()

