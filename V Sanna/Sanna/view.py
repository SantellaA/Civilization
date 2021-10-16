import random, sys, copy, os, pygame, math
from pygame.locals import *
from board import Board
from character import Character

class Graphic():

    def __init__(self):
        self.winWidth = 800 # Ancho de la ventana en pixeles
        self.winHeight = 600 # Alto de la ventana
        self.half_winWIdth = int(self.winWidth/2)
        self.half_winHeight = int(self.winHeight/2)

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()

        self.board = None

        # El ancho y el alto de cada casilla en pixeles
        self.tileWidth = 32
        self.tileHeight = 32

        # Genera la ventana donde se muestra el juego
        self.screen = pygame.display.set_mode((self.winWidth, self.winHeight))

        # Define la velocidad de movimiento de la camara
        self.cameraMove = 0.5

        # Diccionario con las imagenes a cargar en base al caracter escrito en el txt
        self.biomeTiles = {"X": pygame.image.load("floor/Dirt.png"),
                    "Y": pygame.image.load("floor/Mountain.png"),
                    "M": pygame.image.load("floor/Water.png"),
                    " X": pygame.image.load("floor/Dirt_inactive.png"),
                    " Y": pygame.image.load("floor/Mountain_inactive.png"),
                    " M": pygame.image.load("floor/Water_inactive.png"),
                    " ": pygame.image.load("floor/off_world.png")}
        
        self.mapObj = self.readMap("maps/map1.txt")

        # Crea el tablero en la clase board
        self.createBoard()
        self.character = None
        self.runGame()

    def runGame(self):
        mapWidth = len(self.mapObj) * self.tileWidth
        mapHeight = len(self.mapObj[0]) * self.tileHeight
        mapNeedRedraw = True # verdadero para qe llame a drawMap()

        for x in range(2):
            posX, posY = self.setPositionRandom(len(self.mapObj), len(self.mapObj[0]))
            self.board.createUnit(posX, posY)
            self.character = self.board.getUnit(posX, posY)

        # Registra cuanto se movio la camara de su punto original
        cameraSetOffX = 0
        cameraSetOffY = 0 

        #Permite saber si se presiono el mouse
        mousePressed = False

        # Establece el limite de hasta donde puede moverse la camara
        max_cam_move_X = abs(self.half_winWIdth - int(mapWidth/2))
        max_cam_move_Y = abs(self.half_winHeight - int(mapHeight/2))

        # Rastrea si las teclas para mover la camara estan presionadas 
        cameraUp = False
        cameraDown = False
        cameraLeft = False
        cameraRight = False

        # Comienza el loop del juego hasta que el juegador cierre el juego
        while True: 

            #Obtiene la posicion del mouse
            mousePos = pygame.mouse.get_pos()

            # Registra y obtiene todos los eventos que realizo el usuario como un click o apretar una tecla
            for event in pygame.event.get():
                if event.type == QUIT:
                    # El usuario presiono la "X" para cerrar la aplicacion
                    self.terminate()
                
                # Maneja las teclas que fueron presionadas
                if event.type == KEYDOWN:
                    if event.key == K_a:
                        cameraLeft = True
                    if event.key == K_d:
                        cameraRight = True
                    if event.key == K_s:
                        cameraDown = True
                    if event.key == K_w:
                        cameraUp = True
                        
                    if event.key == K_UP:
                        posX, posY = self.character.getPosition()
                        if self.movementPosible(posX, posY - 1):
                            self.board.removeUnitCell(posX, posY)
                            self.board.assignUnitCell(posX , posY - 1, self.character)    
                            self.character.setPosition(posX, posY - 1)
                            mapNeedRedraw = True
                    elif event.key == K_DOWN:
                        posX, posY = self.character.getPosition()
                        if self.movementPosible(posX, posY + 1):
                            self.board.removeUnitCell(posX, posY)
                            self.board.assignUnitCell(posX, posY + 1, self.character)    
                            self.character.setPosition(posX, posY + 1)
                            mapNeedRedraw = True
                    if event.key == K_LEFT:
                        posX, posY = self.character.getPosition()
                        if self.movementPosible(posX - 1, posY):
                            self.board.removeUnitCell(posX, posY)
                            self.board.assignUnitCell(posX - 1, posY, self.character)    
                            self.character.setPosition(posX - 1, posY)
                            mapNeedRedraw = True
                    elif event.key == K_RIGHT:
                        posX, posY = self.character.getPosition()
                        if self.movementPosible(posX + 1, posY):
                            self.board.removeUnitCell(posX, posY)
                            self.board.assignUnitCell(posX + 1, posY, self.character)                            
                            self.character.setPosition(posX + 1, posY)
                            mapNeedRedraw = True
                    
                # Maneja las teclas que fueron soltadas
                if event.type == KEYUP:
                    if event.key == K_a:
                        cameraLeft = False                    
                    if event.key == K_d:
                        cameraRight = False
                    if event.key == K_w:
                        cameraUp = False
                    if event.key == K_s:
                        cameraDown = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousePressed = True

            # Si mapNeedRedraw entonces se recarga el mapa
            if mapNeedRedraw:
                mapSurf = self.writeMap()
                mapNeedRedraw = False
            
            # Cambia la variable del movimiento de la camara si el usuario presiono la tecla y no supera el limite
            if cameraUp and cameraSetOffY < max_cam_move_Y:
                cameraSetOffY += self.cameraMove
            if cameraDown and cameraSetOffY > -max_cam_move_Y:
                cameraSetOffY -= self.cameraMove
            if cameraLeft and cameraSetOffX < max_cam_move_X:
                cameraSetOffX += self.cameraMove
            if cameraRight and cameraSetOffX > -max_cam_move_X:
                cameraSetOffX -= self.cameraMove

            # Ajusta el centro del mapa segun que tanto lo movio el usuario del centro
            mapRect = mapSurf.get_rect()
            mapRect.center = (self.half_winWIdth + cameraSetOffX, self.half_winHeight + cameraSetOffY)

            # Obtiene la posicion de arriba a la izquierda del mapa, donde esta ubicada la camara
            mapRectX, mapRectY = mapRect.topleft
            topLeftPos = abs(mapRectX), abs(mapRectY)

            # Suma dos tuplas
            mousePos = tuple(sum(x) for x in zip(mousePos, topLeftPos))

            if mousePressed:
                posX, posY = mousePos
                unit = self.board.getUnit(math.floor(posX/32), math.floor(posY/32))
                if unit != None:
                    self.character = unit
                mousePressed = False

            self.screen.fill((0,0,0))

            # Dibuja el mapa en la pantalla del display
            self.screen.blit(mapSurf, mapRect)

            pygame.display.update()
            self.FPSCLOCK.tick()

    def createBoard(self):
        """Crea el tablero de la clase board y le asigna el bioma a cada celda"""
        self.board = Board()
        self.board.assignSize(len(self.mapObj))
        for x in range(len(self.mapObj)):
            for y in range(len(self.mapObj[0])):
                self.board.addCellAndBiome(x, y, self.mapObj[x][y])

    def writeMap(self):
        """Crea una superficie y dibuja sobre ella el mapa ingresado 
        dibujando casillas por casilla para luego devolverlo e
        actualizarlo en la pantalla principal"""

        mapWidth = len(self.mapObj) * self.tileWidth
        mapHeight = len(self.mapObj[0]) * self.tileHeight
        
        # Crea una superficie donde dibujar el mapa
        mapSurf = pygame.Surface((mapWidth, mapHeight))

        self.board.hideAllCells()

        unitList = self.board.getListUnits()

        # Revela todas las celdas alrededor de todas las unidades que haya
        for unit in range(len(unitList)):            
            positionX, positionY = unitList[unit].getPosition() # Obtiene la posicion del personaje
            for x in range(len(self.mapObj)):
                for y in range(len(self.mapObj[x])):

                    if ((x - positionX)**2 + (y - positionY)**2)**(1/2) <= 3:
                        self.board.revealCell(x, y) 

        # Dibuja todas las casillas del mapa generando una superficie nueva 
        for x in range(len(self.mapObj)):
            for y in range(len(self.mapObj[x])):

                if ((x - positionX)**2 + (y - positionY)**2)**(1/2) <= 3:
                    self.board.revealCell(x, y) 
                                    
                if self.board.getVisibility(x, y) == (True, True):                
                    spaceRect = pygame.Rect(x*self.tileWidth, y*self.tileHeight, self.tileWidth, self.tileHeight)
                    baseTile = self.biomeTiles[self.board.checkBiome(x, y)]

                    # Dibuja el la casilla con el bioma en la superficie
                    mapSurf.blit(baseTile, spaceRect)
                else:
                    if self.board.getVisibility(x, y) == (False, True):
                        spaceRect = pygame.Rect(x*self.tileWidth, y*self.tileHeight, self.tileWidth, self.tileHeight)
                        baseTile = self.biomeTiles[" " + self.board.checkBiome(x, y)]

                        # Dibuja el la casilla con el bioma en la superficie
                        mapSurf.blit(baseTile, spaceRect)
                    else:
                        spaceRect = pygame.Rect(x*self.tileWidth, y*self.tileHeight, self.tileWidth, self.tileHeight)
                        baseTile = self.biomeTiles[" "]

                        # Dibuja el la casilla con el bioma en la superficie
                        mapSurf.blit(baseTile, spaceRect)

        # Dibuja al personaje 
        for unit in range(len(unitList)):
            positionX, positionY = unitList[unit].getPosition()
            spaceRect = pygame.Rect(positionX * self.tileWidth, positionY * self.tileHeight, self.tileWidth, self.tileHeight)
            baseCharacter = pygame.image.load("characters/Main.png")
            mapSurf.blit(baseCharacter, spaceRect)
        
        return mapSurf

    def readMap(self, file):
        """Agarra el archivo de texto ingresado lo busca y si lo encuentra,
        lo lee y obtiene la informacion de las lineas de texto relacionadas con el mapa
        para luego tranferir los datos de las lineas a una matriz generada en la funcion."""
        # Verifica que exista el archivo y si existe abre el archivo
        assert os.path.exists(file), 'Cannot find the level file: %s' % (file)
        mapFile = open(file, "r")

        # Almacena la informacion de adentro y cierra el archivo
        content = mapFile.readlines() + ["\r\n"]
        mapFile.close()

        mapTextLines = []
        mapObject = []

        # Lee cada linea del archivo de texto
        for lineNum in range(len(content)):
            line = content[lineNum].rstrip('\r\n')

            # Si encuentra un ";" en la linea actual devuelve ""
            if ";" in line:
                line = line[:line.find(";")]

            # Si tiene algo lo añade a la lista con las lineas de texto del mapa
            if line != "":
                mapTextLines.append(line)
            elif line == "" and len(mapTextLines) > 0:
                maxWidth = -1
                # Busca la fila mas larga de todas
                for i in range(len(mapTextLines)):
                    if len(mapTextLines[i]) > maxWidth:
                        maxWidth = len(mapTextLines[i])
                # Las empareja llenando con espacios si es que hace falta
                for i in range (len(mapTextLines)):
                    mapTextLines[i] += " " * (maxWidth - len(mapTextLines[i]))
                # Añade una lista por cada linea de mapa
                for x in range (len(mapTextLines[0])):
                    mapObject.append([])
                # Invierte el mapa para que quede al derecho en la matriz
                for y in range (len(mapTextLines)):
                    for x in range (maxWidth):
                        mapObject[x].append(mapTextLines[y][x])

        return mapObject

    def movementPosible(self, posX, posY):
        """Obtiene el bioma de la celda y si es posible caminar sobre el devuelve True
        de lo contrario devuelve False"""
        if posX >= 0 and posY >= 0:
            try:
                biome = self.board.checkBiome(posX, posY)
                unit = self.board.getUnit(posX, posY)
                if biome == "X" and unit == None:
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def setPositionRandom(self, width, height):
        # Selecciona de mandera aleatoria 2 posiciones para spawnear
        while True:
            positionX = random.randrange(0, width + 1)
            positionY = random.randrange(0, height + 1)
            if self.movementPosible(positionX, positionY) == True:
                break
        return positionX, positionY

    def terminate(self):
        """Finaliza el programa y cierra todo"""
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    start = Graphic()