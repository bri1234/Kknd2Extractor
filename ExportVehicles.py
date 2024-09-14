# -*- coding: utf-8 -*-

class Vehicle:

    # type 1 ... 7
    Type : int
    Id : int
    Name : str
    Price : int

class VehiclesArmy:

    # Survivors, Evolved, Series9
    Army : str
    Units : list[Vehicle]

    def __init__(self, army : str) -> None:
        self.Army = army
        self.Units = []

class Vehicles:

    Survivers : VehiclesArmy
    Evolved : VehiclesArmy
    Series9 : VehiclesArmy

    def __init__(self) -> None:
        self.Survivers = VehiclesArmy("Survivers")
        self.Evolved = VehiclesArmy("Evolved")
        self.Series9 = VehiclesArmy("Series9")

def ExportVehicles() -> Vehicles:

    vehicles = Vehicles()



    return vehicles