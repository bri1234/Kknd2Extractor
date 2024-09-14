# -*- coding: utf-8 -*-

from typing import Any
import KkndFileContainer as container

def InfanteryUnit(fileList : container.ContainerFileType, id : int, name : str, price : int) -> dict[str, Any]:

    return {
        "Id": id,
        "Name": name,
        "Price": price
    }

def ExportSurvivors(fileList : container.ContainerFileType) -> dict[str, Any]:

    return {
        "Army": "Survivors",
        "Units": [
            InfanteryUnit(fileList, 1, "Machine gunner", 100),
            InfanteryUnit(fileList, 2, "Grenadier", 125),
            InfanteryUnit(fileList, 3, "Flamer", 200),
            InfanteryUnit(fileList, 4, "Rocketeer", 200),
            InfanteryUnit(fileList, 5, "Kamikaze", 250),
            InfanteryUnit(fileList, 6, "Laser rifleman", 250),
            InfanteryUnit(fileList, 7, "Technician", 100)
        ]
    }

def ExportEvolved(fileList : container.ContainerFileType) -> dict[str, Any]:
    return {
        "Army": "Evolved",
        "Units": [
            InfanteryUnit(fileList, 1, "Berzerker", 100),
            InfanteryUnit(fileList, 2, "Rioter", 125),
            InfanteryUnit(fileList, 3, "Pyromaniac", 200),
            InfanteryUnit(fileList, 4, "Homing bazookoid", 200),
            InfanteryUnit(fileList, 5, "Martyr", 250),
            InfanteryUnit(fileList, 6, "Spirit archer", 250),
            InfanteryUnit(fileList, 7, "Mekanik", 100)
        ]
    }

def ExportSeries9(fileList : container.ContainerFileType) -> dict[str, Any]:
    return {
        "Army": "Series9",
        "Units": [
            InfanteryUnit(fileList, 1, "Seeder", 250),
            InfanteryUnit(fileList, 2, "Pod launcher", 300),
            InfanteryUnit(fileList, 3, "Weed killer", 450),
            InfanteryUnit(fileList, 4, "Spore missile", 450),
            InfanteryUnit(fileList, 5, "Michelangelo", 500),
            InfanteryUnit(fileList, 6, "Steriliser", 600),
            InfanteryUnit(fileList, 7, "Systech", 100)
        ]
    }
    
def ExportInfantery(fileList : container.ContainerFileType) -> dict[str, Any]:

    return {
        "Survivors": ExportSurvivors(fileList),
        "Evolved": ExportEvolved(fileList),
        "Series9": ExportSeries9(fileList)
    }

