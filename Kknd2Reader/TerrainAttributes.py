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

from enum import Enum

class ETerrainAttribute(Enum):
    OPEN = 0

    NO_GO = 1
    NO_BUILD = 2
    IMPASSABLE = 3
    TREES = 4
    INFANTRY_ONLY = 5
    ROAD = 6
    SWAMP = 7

    SHALLOW_WATER = 8
    MEDIUM_WATER = 9
    DEEP_WATER = 10

    CLIFF_SOUTH = 11
    CLIFF_NORTH = 12
    CLIFF_WEST = 13
    CLIFF_EAST = 14
    CLIFF_NORTH_WEST = 15
    CLIFF_NORTH_EAST = 16
    CLIFF_SOUTH_WEST = 17
    CLIFF_SOUTH_EAST = 18

    DOWNHILL_SOUTH = 19
    DOWNHILL_NORTH = 20
    DOWNHILL_WEST = 21
    DOWNHILL_EAST = 22
    DOWNHILL_NORTH_WEST = 23
    DOWNHILL_NORTH_EAST = 24
    DOWNHILL_SOUTH_WEST = 25
    DOWNHILL_SOUTH_EAST = 26

    DOWNHILL_ROAD_SOUTH = 27
    DOWNHILL_ROAD_NORTH = 28
    DOWNHILL_ROAD_WEST = 29
    DOWNHILL_ROAD_EAST = 30
    DOWNHILL_ROAD_NORTH_WEST = 31
    DOWNHILL_ROAD_NORTH_EAST = 32
    DOWNHILL_ROAD_SOUTH_WEST = 33
    DOWNHILL_ROAD_SOUTH_EAST = 34

    UNDERGROUND = 35

