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
import numpy as np
import numpy.typing as npt

import tkinter as tk
from tkinter import ttk
import threading

import KkndFileMapd as mapd

LayerList : list[npt.NDArray[np.uint32]] = []
PhotoImg : tk.PhotoImage
ListboxLayers : tk.Listbox
Progress : tk.IntVar

def SetPixel(img : tk.PhotoImage, x : int, y : int, colorRgb : int) -> None:
    img.put( f"#{colorRgb & 0xFFFFFF:06X}", ( x, y ) )

def DrawLayer(photoImg : tk.PhotoImage, layer : npt.NDArray[np.uint32]) -> None:
    global Progress

    width = layer.shape[0]
    height = layer.shape[1]
    dataStr : list[str] = []

    Progress.set(0)

    for row in range(height):

        dataStr.append("{")

        for column in range(width):
            dataStr.append(f"#{layer[column, row]:06X}")

        dataStr.append("}")
        Progress.set( int((row + 1) / height * 100.0))

    photoImg.put( " ".join(dataStr), ( 0, 0 ) )

def ShowLayer(layerIndex : int) -> None:
    global LayerList, PhotoImg, ListboxLayers

    PhotoImg.blank()
    DrawLayer(PhotoImg, LayerList[layerIndex])
    ListboxLayers.configure(state=tk.NORMAL)

def ListBoxFileSelected(event : Any) -> None:
    selection : int = event.widget.curselection()[0]
    event.widget.configure(state=tk.DISABLED)
    threading.Thread(target=ShowLayer, args=(selection,)).start()

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
    global LayerList, PhotoImg, ListboxLayers, Progress

    maps = mapd.ReadMaps("assets/multiplayermap/mlti_12.lpm")

    window = tk.Tk()
    PhotoImg, ListboxLayers, Progress = BuildGui(window, 10000, 10000)

    LayerList.clear()
    for idxMap in range(len(maps)):
        map = maps[idxMap]

        for idxLayer in range(len(map.LayerList)):
            renderedLayer = map.RenderLayer(idxLayer)
            LayerList.append(renderedLayer)
            ListboxLayers.insert(tk.END, f"Map {idxMap} Layer {idxLayer}")

    tk.mainloop()

if __name__ == "__main__":
    
    Main()

