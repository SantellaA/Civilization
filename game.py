import pygame, sys
from pygame import rect
from pygame.locals import *
"""-----------------------------------------------------------------------------"""
import random, math,os
from world import World
"""-----------------------------------------------------------------------------"""
import pygame
from pygame.locals import *

class Controller():

    def __init__(self):
        """Loads the variables and execute the methods when the class is created"""
        pygame.init()

        self.view = View()
        self.model = Model()
        self.view.setModel(self.model)
        self.model.randomMap(100, 80)
        self.model.readMap("Maps/random_world.txt")
        self.view.setMapSize()
        self.model.randomUnitGeneration()
        self.model.randomUnitGeneration()
        self.model.revealMap()
        self.view.drawMap()
        self.view.centerLoadCamera()
        self.loopGame()
    
    def loopGame(self):
        """Loop of the game which gets the inputs of the user"""
        camUp = False
        camDown = False
        camRight = False
        camLeft = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #If the user presses the X at the top right
                    self.terminate()
        
                if event.type == KEYDOWN:
                    #When the arrows are pressed
                    if event.key == K_UP:
                        camUp = True
                    if event.key == K_DOWN:
                        camDown = True
                    if event.key == K_RIGHT:
                        camRight = True
                    if event.key == K_LEFT:
                        camLeft = True

                    #When the enter is pressed 
                    if event.key == K_RETURN:
                        self.model.passTurn()
                        self.view.mapNeedsRedraw()

                    #When the leters w,a,s,d are pressed
                    if event.key == K_w:
                        self.model.moveUnit(0, -1)
                        self.model.setPositionToMoveUnit(None, None)
                        self.view.mapNeedsRedraw()
                    if event.key == K_s:
                        self.model.moveUnit(0, 1)
                        self.model.setPositionToMoveUnit(None, None)
                        self.view.mapNeedsRedraw()
                    if event.key == K_a:
                        self.model.moveUnit(-1, 0)
                        self.model.setPositionToMoveUnit(None, None)
                        self.view.mapNeedsRedraw()
                    if event.key == K_d:
                        self.model.moveUnit(1, 0)
                        self.model.setPositionToMoveUnit(None, None)
                        self.view.mapNeedsRedraw()

                #When the arrows stopped being pressed
                if event.type == KEYUP:
                    if event.key == K_UP:
                        camUp = False
                    if event.key == K_DOWN:
                        camDown = False
                    if event.key == K_RIGHT:
                        camRight = False
                    if event.key == K_LEFT:
                        camLeft = False

                #When the mouse is clicked
                if event.type == MOUSEBUTTONDOWN:
                    mousePos = pygame.mouse.get_pos()
                    posX, posY = self.view.getMouseMapPos(mousePos)
                    if pygame.mouse.get_pressed()[0]: # Left click
                        if not self.view.drawUnitActions(mousePos, True):
                            self.model.cellSelected(posX, posY)
                            self.view.mapNeedsRedraw()
                    if pygame.mouse.get_pressed()[2]: # Right click
                        self.model.setPositionToMoveUnit(posX, posY)
                        

            if camUp:
                self.view.moveCamera("U")
            if camDown:
                self.view.moveCamera("D")
            if camRight:
                self.view.moveCamera("R")
            if camLeft:
                self.view.moveCamera("L")
                
            self.view.updateScreen()

    def terminate(self):
        """End the program"""
        pygame.quit()
        sys.exit()
   
class View():

    def __init__(self):
        """Loads the variables and execute the methods when the class is created"""
        pygame.init()

        self.model = None

        self.screenWidth = 1280 
        self.screenHeight = 672
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight)) #Creates the screen where the game will display

        #Store the width and height fo the map
        self.mapWidth = None 
        self.mapHeight = None

        #Store the width and height of the cells
        self.tileWidth = 32
        self.tileHeight = 32

        self.mapSurf = None
        self.mapRect = None

        #Gets the image of the cell from the string
        self.textToMap = {"B" : pygame.image.load("asets/floor/Barrier.png"),
                            "D" : pygame.image.load("asets/floor/Dirt.png"),
                            " D": pygame.image.load("asets/floor/Dirt_inactive.png"),
                            "F" : pygame.image.load("asets/floor/Forest.png"),
                            " F" : pygame.image.load("asets/floor/Forest_inactive.png"),
                            "W" :pygame.image.load("asets/floor/Water.png"),
                            " W" :pygame.image.load("asets/floor/Water_inactive.png"),
                            "M" : pygame.image.load("asets/floor/Mountain.png"),
                            " M" : pygame.image.load("asets/floor/Mountain_inactive.png"),
                            "I" : pygame.image.load("asets/floor/Iron_Mountain.png"),
                            " I" : pygame.image.load("asets/floor/Iron_Mountain_inactive.png"),
                            "G" : pygame.image.load("asets/floor/Gold_Mountain.png"),
                            " G" : pygame.image.load("asets/floor/Gold_Mountain_inactive.png"),
                            "": pygame.image.load("asets/floor/off_world.png"),
                            "R" : "Revealed",
                            "H" : "Hidden",
                            "0" : False,
                            "1" : True}
        
        #Gets the image of the unit from the string
        self.textToUnit = {
            "WR" : pygame.image.load("asets/characters/Red_Warrior.png"),
            "FD" : pygame.image.load("asets/characters/Red_Founder.png"),
            "WK" : pygame.image.load("asets/characters/Red_worker.png")
        }

        #Dictionary with the menu of actions of each unit
        self.unitMenu = {
            "FD" : self.founderActions
        }

        self.unit = None

        #Sets the limit for the camera to move
        self.maxCamMoveX = None
        self.maxCamMoveY = None

        #Stores how much the camera move fron the center
        self.cameraMoveX = 0
        self.cameraMoveY = 0    

        self.cameraVelocity = 5 #Sets the velocity of the camera movement    

    def setModel(self, model):
        """Sets the same model that uses the controller"""
        self.model = model
    
    def setMapSize(self):
        """Sets the map width, height and all the variables which need this information"""
        self.mapWidth, self.mapHeight = self.model.getWidthHeight()
        
        self.mapSurf = pygame.Surface((self.mapWidth * self.tileWidth, self.mapHeight * self.tileHeight)) #Creates a surface for the map
        
        self.maxCamMoveX = abs(self.screenWidth / 2 - self.mapWidth * self.tileWidth / 2)
        self.maxCamMoveY = abs(self.screenHeight / 2 - self.mapHeight * self.tileHeight / 2)

    def drawMap(self):
        """Draws the map on a surface"""
        for x in range(self.mapWidth):
            for y in range(self.mapHeight):
                #Gets the biome of the cell and draw it on the surface
                visibility = self.model.getCellVisibility(x, y)
                biome, unit = self.model.getCellData(x, y)
                if visibility == (True, True):
                    baseTile = self.textToMap[biome]
                    tileRect = pygame.Rect(x * self.tileWidth, y * self.tileHeight, self.tileWidth, self.tileHeight)
                    self.mapSurf.blit(baseTile, tileRect)
                    if unit != None:
                        unitImage = self.textToUnit[str(unit)]
                        self.mapSurf.blit(unitImage, tileRect) #Draws the unit on the cell
                        health, maxHealth = self.model.getUnitHealth(unit)
                        relationHealthBar = health/maxHealth

                        heightBar = 6
                        healthBar = pygame.Surface((self.tileWidth, heightBar))
                        healthBarRect = pygame.Rect(tileRect[0], tileRect[1] + self.tileHeight - heightBar, self.tileWidth, heightBar)

                        colorHealthBar = pygame.Surface(((self.tileWidth - 2) * relationHealthBar, heightBar - 2))
                        colorHealthBar.fill((255, 0, 0))
                        colorHealthBarRect = colorHealthBar.get_rect(topleft = (healthBarRect[0] + 1, healthBarRect[1] + 1))

                        self.mapSurf.blit(healthBar, healthBarRect)
                        self.mapSurf.blit(colorHealthBar, colorHealthBarRect)



                if visibility == (True, False):
                    baseTile = self.textToMap[" " + biome]
                    tileRect = pygame.Rect(x * self.tileWidth, y * self.tileHeight, self.tileWidth, self.tileHeight)
                    self.mapSurf.blit(baseTile, tileRect)
                if visibility == (False, False):
                    baseTile = self.textToMap[""]
                    tileRect = pygame.Rect(x * self.tileWidth, y * self.tileHeight, self.tileWidth, self.tileHeight)
                    self.mapSurf.blit(baseTile, tileRect)

    def mapNeedsRedraw(self):
        if self.model.getMapRedraw():
            self.drawMap()

    def moveCamera(self, cameraDirection):
        """Moves the camera and checks if it can move also"""
        if cameraDirection == "U" and self.cameraMoveY < self.maxCamMoveY:
            self.cameraMoveY += self.cameraVelocity
        if cameraDirection == "D" and self.cameraMoveY > -self.maxCamMoveY:
            self.cameraMoveY -= self.cameraVelocity
        if cameraDirection == "L" and self.cameraMoveX < self.maxCamMoveX:
            self.cameraMoveX += self.cameraVelocity
        if cameraDirection == "R" and self.cameraMoveX > -self.maxCamMoveX:
            self.cameraMoveX -= self.cameraVelocity

    def centerLoadCamera(self):
        posX, posY = self.model.getPositionUnit()
        if posX < self.mapWidth/2:
            self.cameraMoveX += abs(posX - self.mapWidth/2) * self.tileWidth
        else:
            self.cameraMoveX -= abs(posX - self.mapWidth/2) * self.tileWidth
        if posY < self.mapHeight/2:
            self.cameraMoveY += abs(posY - self.mapHeight/2) * self.tileHeight
        else:
            self.cameraMoveY -= abs(posY - self.mapHeight/2) * self.tileHeight
        if self.cameraMoveY > self.maxCamMoveY:
            self.cameraMoveY = self.maxCamMoveY
        elif self.cameraMoveY < -self.maxCamMoveY:
            self.cameraMoveY = -self.maxCamMoveY 
        if self.cameraMoveX > self.maxCamMoveX:
            self.cameraMoveX = self.maxCamMoveX 
        elif self.cameraMoveX < -self.maxCamMoveX:
            self.cameraMoveX = -self.maxCamMoveX

    def getMouseMapPos(self, mousePos):
        """Gets the mouse position in relation of the map Surface"""
        rectX, rectY = self.mapRect.topleft        
        mousePos = tuple(sum(x) for x in zip(mousePos, (abs(rectX), abs(rectY))))
        posX, posY = mousePos
        return math.floor(posX/self.tileWidth), math.floor(posY/self.tileHeight)

    def updateScreen(self):
        self.screen.fill((0,0,0))
        self.mapRect = self.mapSurf.get_rect(center = (self.screenWidth/2 + self.cameraMoveX, self.screenHeight/2 + self.cameraMoveY))  
        self.screen.blit(self.mapSurf, self.mapRect)   
        self.drawUnitActions((0, 0), False)
        pygame.display.update()

    def founderActions(self, mousePos, click):
        """Draws the button with the possible action of the founder unit"""
        defendIcon = pygame.image.load("asets/buttons/rest_button.png")
        iconRect = pygame.Rect(self.screenWidth - self.tileWidth*2, self.screenHeight - self.tileHeight, self.tileWidth, self.tileHeight)
        self.screen.blit(defendIcon, iconRect)
        if iconRect.collidepoint(mousePos) and click == True:
            self.unit = None
            self.model.setUnitMenu(None)
            self.model.setAttack(True)
            return True

        attackIcon = pygame.image.load("asets/buttons/battle_button.png")
        iconRect = pygame.Rect(self.screenWidth - self.tileWidth*4, self.screenHeight - self.tileHeight, self.tileWidth, self.tileHeight)
        self.screen.blit(attackIcon, iconRect)
        if iconRect.collidepoint(mousePos) and click == True:
            self.unit = None
            self.model.setUnitMenu(None)
            self.model.setAttack(True)
            return True

        foundIcon = pygame.image.load("asets/buttons/found_button.png")
        iconRect = pygame.Rect(self.screenWidth - self.tileWidth*6, self.screenHeight - self.tileHeight, self.tileWidth, self.tileHeight)
        self.screen.blit(foundIcon, iconRect)
        if iconRect.collidepoint(mousePos) and click == True:
            self.unit = None
            self.model.setUnitMenu(None)
            self.model.setAttack(True)
            return True
        
    def drawUnitActions(self, mousePos, click):
        self.unit = self.model.getUnitMenu()
        if self.unit != None:
            return self.unitMenu[self.unit](mousePos, click)

class Model():

    def __init__(self):
        """Loads the variables and execute the methods when the class is created"""
        self.world = World()

        self.mapWidth = None
        self.mapHeight = None

        self.mapNeedsRedraw = False

        self.actualUnit = None
        self.unitMenu = None

        self.attack = None #Saves is a unit is going to attack

    def setAttack(self, value):
        """Sets the attack event"""
        self.attack = value

    def randomMap(self, width, height):
        """Generates a txt with a random map"""
        self.world.setWorldSize(width, height)
        self.world.random_world()

    def readMap (self, file):
        """Reads a txt file with the map"""
        assert os.path.exists(file), 'Cannot find the level file: %s' % (file)
        M_File = open(file, "r")
        content = M_File.readlines() + ["\r\n"]
        M_File.close()

        M_TextLines = []
        M_Obj = []

        for lineNum in range(len(content)):
            line = content[lineNum].rstrip('\r\n')

            # Si encuentra un ";" en la linea actual devuelve ""
            if ";" in line:
                line = line[:line.find(";")]

            # Si tiene algo lo añade a la lista con las lineas de texto del mapa
            if line != "":
                M_TextLines.append(line)

            elif line == "" and len(M_TextLines) > 0:
                maxWidth = -1

                # Busca la fila mas larga de todas
                for i in range(len(M_TextLines)):
                    if len(M_TextLines[i]) > maxWidth:
                        maxWidth = len(M_TextLines[i])

                # Las empareja llenando con espacios si es que hace falta
                for i in range (len(M_TextLines)):
                    M_TextLines[i] += " " * (maxWidth - len(M_TextLines[i]))

                # Añade una lista por cada linea de mapa
                for x in range (len(M_TextLines[0])):
                    M_Obj.append([])

                # Invierte el mapa para que quede al derecho en la matriz
                for y in range (len(M_TextLines)):
                    for x in range (maxWidth):
                        M_Obj[x].append(M_TextLines[y][x])
                
        self.createBoard(M_Obj)

    def createBoard(self, M_Obj):
        """Crea el tablero de la clase board y le asigna el bioma a cada celda"""

        self.world.assignSize(len(M_Obj))

        for x in range(len(M_Obj)):
            for y in range(len(M_Obj[0])):
                self.world.addCellAndBiome(x, y, M_Obj[x][y])
        
        self.world.updateNeighbors()

    def getWidthHeight(self):
        """Gets the width and height of the actual map"""
        self.mapWidth, self.mapHeight = self.world.getWidthHeight()
        return self.mapWidth, self.mapHeight

    def getCellBiome(self, x, y):
        """Gets the biome of the cell"""
        biome = self.world.getBiome(x,y)
        return biome

    def getCellData(self, x, y):
        """Gets the biome and the unit of the cell"""
        return self.world.getCellData(x, y)

    def assignNewUnitCell(self, x, y, type):
        """Asigns a new unit to a cell"""
        self.world.assignNewUnit(x, y, type)
        self.getAndAssignUnit(x, y)
        self.actualUnit.restartMovement()
        self.setUnitMenu(str(self.actualUnit))

    def reassignUnitCell(self, posX, posY, newPosX, newPosY):
        """reassign a unit from one cell to other"""
        self.world.reassignUnit(posX, posY, newPosX, newPosY)

    def moveUnit(self, x, y):
        """Checks if a unit can move and if so it does"""
        posX, posY = self.actualUnit.getPosition()
        if self.actualUnit.getMovement() > 0:
            if self.movementPossible(posX + x, posY + y):
                self.actualUnit.reduceMovement()
                self.reassignUnitCell(posX, posY, posX + x, posY + y)
                self.hideMap()
                self.revealMap()
                self.mapNeedsRedraw = True

    def getAndAssignUnit(self, x, y):
        """Gets the unit of a cell and assign it as the active unit"""
        unit = self.world.getUnit(x, y)
        if unit != None:
            self.actualUnit = unit
            self.setUnitMenu(str(self.actualUnit))

    def randomUnitGeneration(self):
        """Selects a random position on the map"""
        while True:
            posX = random.randrange(0, self.mapWidth)
            posY = random.randrange(0, self.mapHeight)
            if self.movementPossible(posX, posY):
                break
        self.assignNewUnitCell(posX, posY, "FD")

    def movementPossible(self, x, y):
        """Checks if it is possible to move to the cell"""
        try:
            biome, unit = self.getCellData(x, y)
            if biome == "D" and unit == None and x >= 0 and y >= 0:
                return True
            else:
                return False
        except:
            return False

    def getMapRedraw(self):
        """Return if the map needs to redraw or not"""
        if self.mapNeedsRedraw:
            self.mapNeedsRedraw = False
            return True
        else:
            return False

    def hideMap(self):
        """Hide the map"""
        self.world.hideAllCells()

    def revealMap(self):
        """Reveal the part of the map seen by all the units"""
        self.world.revealMap()

    def getCellVisibility(self, x, y):
        """Gets if a cell was revealed and if it is actually being seen"""
        return self.world.getCellVisibility(x, y)

    def getPositionUnit(self):
        return self.actualUnit.getPosition()

    def restartAllUnitMovement(self):
        """Restarts the movement of all the units"""
        self.world.restartAllUnitMovement()   

    def setUnitMovement(self, posX, posY):
        """Sets the position to move of the unit selected"""
        self.actualUnit.setPostionToMove(posX, posY)

    def moveUnits(self):
        """Gets the position and routes of units and moves them"""
        actualUnit = self.actualUnit
        units = self.world.getAllUnits()

        for unit in units:   

            self.actualUnit = unit
            routes = unit.getRoute()
            routesReverted = []

            #Reverts the list
            for x in range(1, len(routes) + 1):
                routesReverted.append(routes[-x])
            routes = routesReverted

            if routes != None:
                for route in routes:
                    posX, posY = unit.getPosition()
                    if self.actualUnit.getMovement() > 0:                        
                        posToMoveX, posToMoveY = route
                        self.moveUnit(posToMoveX - posX, posToMoveY - posY)
                        if route == self.actualUnit.getPositionToMove(): # Checks if the actual route is the final position
                            self.setPositionToMoveUnit(None, None)
                    else:
                        break
        self.actualUnit = actualUnit

    def setPositionToMoveUnit(self, posX, posY):
        """Sets the position to move of the unit"""            
        self.actualUnit.setPostionToMove(posX, posY)

    def getUnitMenu(self):
        """Gets the string of the actual unit"""
        return self.unitMenu

    def setUnitMenu(self, value):
        """Sets the value of the unitMenu"""
        self.unitMenu = value

    def getUnitHealth(self, unit):
        """Gets the health of the unit"""
        return unit.getHealthData()

    def attackUnit(self, x, y):
        """Attacks if the cell selected has an enemy unit"""
        biome, unit = self.getCellData(x, y)
        if unit != None:
            if self.actualUnit.getActionPosible():
                x1, y1 = self.actualUnit.getPosition()
                x2, y2 = unit.getPosition()
                if abs(x1 - x2) < 2 and abs(y1 - y2) < 2:
                    self.actualUnit.meleeAttack(unit)
        self.attack = False

    def cellSelected(self, x, y):
        """Executes a method depending if an event is active or not"""
        if self.attack:
            self.attackUnit(x, y)
            self.attack = False
            self.mapNeedsRedraw = True
        else:
            self.getAndAssignUnit(x, y)

    def passTurn(self):
        """All that happens when the turned passes is here"""
        self.world.setAllUnitsRoute()
        self.moveUnits()
        self.restartAllUnitMovement()

if __name__ == "__main__":
    game = Controller()