# -*- coding: utf-8 -*-

import KkndFileContainer as container

class InfanteryUnit:

    Id : int
    Name : str
    Price : int

    def __init__(self, id : int, name : str, price : int) -> None:
        self.Id = id
        self.Name = name
        self.Price = price
        
class InfanteryArmy:

    # Survivors, Evolved, Series9
    Army : str
    Units : list[InfanteryUnit]

    def __init__(self, army : str) -> None:
        self.Army = army
        self.Units = []

class Infantery:

    Survivors : InfanteryArmy
    Evolved : InfanteryArmy
    Series9 : InfanteryArmy

    def __init__(self) -> None:
        self.Survivors = InfanteryArmy("Survivors")
        self.Evolved = InfanteryArmy("Evolved")
        self.Series9 = InfanteryArmy("Series9")

def ExportSurvivors() -> list[InfanteryUnit]:

    units : list[InfanteryUnit] = [ InfanteryUnit(1, "Machine gunner", 100),
        InfanteryUnit(2, "Grenadier", 125),
        InfanteryUnit(3, "Flamer", 200),
        InfanteryUnit(4, "Rocketeer", 200),
        InfanteryUnit(5, "Kamikaze", 250),
        InfanteryUnit(6, "Laser rifleman", 250),
        InfanteryUnit(7, "Technician", 100)
    ]

    return units

def ExportEvolved() -> list[InfanteryUnit]:
    units : list[InfanteryUnit] = [ InfanteryUnit(1, "Berzerker", 100),
        InfanteryUnit(2, "Rioter", 125),
        InfanteryUnit(3, "Pyromaniac", 200),
        InfanteryUnit(4, "Homing bazookoid", 200),
        InfanteryUnit(5, "Martyr", 250),
        InfanteryUnit(6, "Spirit archer", 250),
        InfanteryUnit(7, "Mekanik", 100)
    ]

    return units

def ExportSeries9() -> list[InfanteryUnit]:
    units : list[InfanteryUnit] = [ InfanteryUnit(1, "Seeder", 250),
        InfanteryUnit(2, "Pod launcher", 300),
        InfanteryUnit(3, "Weed killer", 450),
        InfanteryUnit(4, "Spore missile", 450),
        InfanteryUnit(5, "Michelangelo", 500),
        InfanteryUnit(6, "Steriliser", 600),
        InfanteryUnit(7, "Systech", 100)
    ]

    return units
    
def ExportInfantery(fileList : list[container.ContainerFile]) -> Infantery:

    infantery = Infantery()

    infantery.Survivors.Units = ExportSurvivors()
    infantery.Evolved.Units = ExportEvolved()
    infantery.Series9.Units = ExportSeries9()

    return infantery