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

import json
from typing import Any

class JsonFlatList:
    """ A list that shall be exported as a float list in JSON.
    """
    _list = None
    def __init__(self, l : Any):
        self._list = l

class __CustomJSONEncoder(json.JSONEncoder):
    """ Helper for pretty JSON export.
    """
    def default(self, o : Any):
        if isinstance(o, JsonFlatList):
            return "##~<{}>~##".format(o._list) # type: ignore
    
def __CorrectOutput(jsonString : str) -> str:
    return jsonString.replace('"##~<[', '[').replace(']>~##"', ']')

def ExportAsJson(obj : Any) -> str:
    """ Exports the object in a JSON string.

    Args:
        obj (Any): The object.

    Returns:
        str: The JSON string.
    """
    jsonStr = json.dumps(obj, indent=2, ensure_ascii=False, cls=__CustomJSONEncoder)
    return __CorrectOutput(jsonStr)

def ExportAsJsonFile(fileName : str, obj : Any) -> None:
    """ Exports the object in a JSON file.

    Args:
        fileName (str): The filename of the JSON file.
        obj (Any): The object.
    """
    jsonStr = ExportAsJson(obj)

    with open(fileName, "w", encoding="utf-8") as file:
        file.write(jsonStr)
