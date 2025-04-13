# Kknd2Extractor

This python scripts are used to extract maps, sprites and sounds from the KKND2 asset files.

Partly based on information from the following projects:

- https://github.com/IceReaper/OpenKrush
- https://github.com/ucosty/kknd2-mapview


# KKND2 files

- ".lpk"  Spritesheet container
- ".bpk"  Image container
- ".spk"  Sound set
- ".lps"  Singleplayer map
- ".lpm"  Multiplayer map
- ".mpk"  Matrix set (destroyable map part, tile replacements)

# Usage

## The map file viewer

Start the KKND2 map file viewer with:

python3 MapViewer.py

(python modules needed: wx, numpy)

- Use "File -> Open map file" to open single or multiplayer maps. (*.lpm or *.lps)
  (it takes a long time to load the map because python is so slow)
- Use "View" to show or hide the different layers.
- Use "Export -> Export map to JSON + PNG" to export the map to a JSON file and two PNG images for bottom and top layer.
  (it takes also some seconds to finish the export)

## The sprite viewer

- is under development ...
