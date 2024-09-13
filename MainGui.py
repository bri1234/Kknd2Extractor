# -*- coding: utf-8 -*-

import tkinter as tk
import KkndFileCompression as compression
import KkndFileContainer as container
import KkndFileMobd as kkndMobd

WIDTH = 1000
HEIGHT = 1000

def SetPixel(img : tk.PhotoImage, x : int, y : int, colorRgb : int) -> None:
    img.put( f"#{colorRgb & 0xFFFFFF:06X}", ( x, y ) )

def DrawImage(image : tk.PhotoImage) -> None:

    containerData, _, _ = compression.UncompressFile("assets/spritesheets/gamesprt.lpk")
    fileTypeList, _ = container.ReadFileTypeList(containerData)

    if fileTypeList[0].FileType != "MOBD":
        return
    
    file = fileTypeList[0].FileList[1]

    mobd = kkndMobd.Mobd()
    mobd.ReadAnimations(file.RawData, file.FileOffset)
    
    offY = 0
    for animation in mobd.AnimationList:

        print(f"Number of frames: {len(animation.FrameList)}")

        offX = 0
        imgHeight = 0
        for frame in animation.FrameList:
            palette = frame.Palette
            img = frame.Image

            for x in range(img.Width):
                for y in range(img.Height):
                    pixel = img.GetPixel(x, y)
                    color = palette.Colors[pixel]

                    SetPixel(image, x + offX, y + offY, color)


            offX += img.Width
            imgHeight = max(imgHeight, img.Height)

        offY += imgHeight

def Main() -> None:

    window = tk.Tk()
    canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="#000000")
    canvas.pack()

    img = tk.PhotoImage(width=WIDTH, height=HEIGHT)
    canvas.create_image((WIDTH / 2, HEIGHT / 2), image=img, state="normal") # type: ignore

    DrawImage(img)

    tk.mainloop()

if __name__ == "__main__":
    
    Main()

