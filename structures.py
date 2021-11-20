class Structures:
    """ Una calse Asentamientos donde estan todos los edificios"""

    def __init__(self):
        """ constructor de la clase """
        self.maxLife = None
        self.life = None
        self.type = ""
        self.x = None
        self.y = None
        self.visibility = None
    
    def __str__(self):
        return self.type
    
    def getRepaired(self):
        """Repairs the structure, healing it"""
        self.life += 3
        if self.maxLife < self.life:
            self.life = self.maxLife
    
    def getHealthData(self):
        return self.life, self.maxLife

    def setPosition(self, posX, posY):
        """Sets the coordinates of the city"""
        self.x = posX
        self.y = posY
    
    def getPosition(self):
        """Gets the position of the structure"""
        return self.x, self.y

    def reciveAttack(self, dmg):
        """Reduces the life of the unit based on the damage received"""
        self.life -= dmg

    def counterAttack(self):
        return 0

    def revealMap(self, map):
        """Reveal all the cells in range of the unit"""
        for x in range(self.x - self.visibility, self.x + self.visibility + 1):
            if x < 0:
                continue
            for y in range(self.y - self.visibility, self.y + self.visibility + 1):
                if y < 0:
                    continue
                try:
                    if ((x - self.x)**2 + (y - self.y)**2)**(1/2) <= self.visibility:
                        map[x][y].revealCell()
                except:
                    continue

class City(Structures):

    def __init__(self):
        super().__init__()
        self.maxLife = 30
        self.life = 2
        self.type = "CT"
        self.production = []
        self.timeProduction = []
        self.actualUnit = None
        self.actualTime = None
        self.visibility = 6
    
    def addUnitProduction(self, unit, time):
        """Adds an unit to the production of it"""
        self.production.append(unit)
        self.timeProduction.append(time)
    
    def productionFinished(self):
        """Checks if an unit finished producing and returns it"""
        if self.actualTime != None:
            if self.actualTime <= 0:
                unit = self.actualUnit
                self.actualUnit = None
                self.actualTime = None
                return unit
            else:
                return None
    
    def reduceTime(self):
        """Reduce the time needed for the unit to be created"""
        if self.actualTime != None:
            if self.actualTime > 0:
                self.actualTime -= 1

    def assignNewUnit(self):
        """When a unit finishes from producing, a new one is assigned"""
        if self.actualUnit == None:
            if self.production != [] and self.timeProduction != []:
                self.actualUnit = self.production[0]
                self.production.pop(0)
                self.actualTime = self.timeProduction[0]
                self.timeProduction.pop(0)          


