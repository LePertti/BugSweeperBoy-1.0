import pygame, sys
from pygame.locals import *
import random

pygame.init()
pygame.display.set_caption("BugSweeperBoy")
clock = pygame.time.Clock()
FPS = 60


# The green colors of GAMEBOY
LIGHTEST  = (155, 188, 15)
LIGHT   = (139, 172, 15)
DARK = (48, 98, 48)
DARKEST = (15, 56, 15)

# Graphics for grid elements
cellimages = {
"UNCLICKEDTILE": pygame.image.load("graphics/simpleunclicked.png"),
"FLAGGED": pygame.image.load("graphics/simpleclickedtile_bug.png"),
"CLICKEDTILE_0": pygame.image.load("graphics/simpleclickedtile_empty.png"),
"CLICKEDTILE_BUG": pygame.image.load("graphics/simpleclickedtile_bug.png"),
"CLICKEDTILE_BUGGED": pygame.image.load("graphics/simpleclickedtile_bugged.png"),
"CLICKEDTILE_1": pygame.image.load("graphics/simpleclickedtile_one.png"),
"CLICKEDTILE_2": pygame.image.load("graphics/simpleclickedtile_two.png"),
"CLICKEDTILE_3": pygame.image.load("graphics/simpleclickedtile_three.png"),
"CLICKEDTILE_4": pygame.image.load("graphics/simpleclickedtile_four.png"),
"CLICKEDTILE_5": pygame.image.load("graphics/simpleclickedtile_five.png"),
"CLICKEDTILE_6": pygame.image.load("graphics/simpleclickedtile_six.png"),
"CLICKEDTILE_7": pygame.image.load("graphics/simpleclickedtile_seven.png"),
"CLICKEDTILE_8": pygame.image.load("graphics/simpleclickedtile_eight.png")
}

#  Visuals
screen = pygame.display.set_mode((1920, 1080))
background = pygame.image.load("graphics/gameboy.png")
menu = pygame.image.load("graphics/simple_meny.png")


# Game Area position and size
GAME_AREA_SIZE = (800, 720)
GAME_AREA_POSITION = (563, 162)

# Menu
MENU_AREA_SIZE =  (50, 800)
MENU_AREA_POSITION = (563, 800)


# Define fonts
FONT = pygame.font.Font('fonts/VT323-Regular.ttf', 30)

# Create a surface for the game area
gameboyscreen = pygame.Surface(GAME_AREA_SIZE)
gameboyscreen.fill(LIGHTEST)

# Grid and Cell Info
PADDING = 2
CELLSIZE = 30 + PADDING # Size of each cell in the grid

COLUMNS = 25
ROWS = 20

BUGS = 60  # The Number of Bugs

game_over = False  # Flag to indicate if the game is over
win_state = False


# Define constants for the reset button
RESET_BUTTON_SIZE = (100, 30)
RESET_BUTTON_POSITION = (MENU_AREA_POSITION[0] + 200, MENU_AREA_POSITION[1] + 25)
RESET_BUTTON_COLOR = pygame.Color(DARK)

WIN_MESSAGE_SIZE = (400, 100)
WIN_MESSAGE_POSITION = (GAME_AREA_POSITION[0] + 200, GAME_AREA_POSITION[1] + 260)
WIN_MESSAGE_BG_COLOR = pygame.Color(DARKEST)


# Initialize the game grid
def initializeGrid(COLUMNS, ROWS):
    gameGrid = {}
    for column in range(COLUMNS):
        
        for row in range(ROWS):
            gameGrid[(column, row)] = {'bug': False, 'revealed': False, 'count': 0, 'flagged': False}
        
    return gameGrid

# Add bugs to the grid
def dropBugs(numBugs, columns, rows, gameGrid):
    bugs = []
    while len(bugs) < numBugs:
        col = random.randint(0, columns - 1)
        row = random.randint(0, rows - 1)
        if (col, row) not in bugs:
            bugs.append((col, row))
            gameGrid[(col, row)]['bug'] = True
    return bugs

# RE-Initialize the game grid and drop the bugs
gameGrid = initializeGrid(COLUMNS, ROWS)
bugs = dropBugs(BUGS, COLUMNS, ROWS, gameGrid)

# Check if there are bugs around
def countAdjacentBugs(gameGrid, bugs, column, row):
    count = 0
    for x in range(max(0, column - 1), min(COLUMNS, column + 2)):
        for y in range(max(0, row - 1), min(ROWS, row + 2)):
            if x != column or y != row:
                if (x, y) in bugs:
                    count += 1
    return count



def drawGrid(gameGrid, gameboyscreen):
    for column, row in gameGrid.keys():
        cellitem = pygame.Rect(column * CELLSIZE, row * CELLSIZE, CELLSIZE, CELLSIZE)
        cellstate = gameGrid[(column, row)]
        if cellstate['flagged']:
            cellimage = cellimages["FLAGGED"]
        elif cellstate['revealed']:
            if cellstate['bug']:
                cellimage = cellimages["CLICKEDTILE_BUGGED"]
            else:
                count = countAdjacentBugs(gameGrid, bugs, column, row)
                cellimage = cellimages[f"CLICKEDTILE_{count}"]
        else:
            cellimage = cellimages["UNCLICKEDTILE"]
        gameboyscreen.blit(cellimage, cellitem)
    pygame.display.update()

drawGrid(gameGrid, gameboyscreen)


def revealAdjacentCells(gameGrid, bugs, column, row, COLUMNS, ROWS):
    # Base case: if the current cell is bugged or already clicked, stop recursion
    if gameGrid[(column, row)].get("revealed") or gameGrid[(column, row)].get("bug"):
        return
    
    # Otherwise, reveal the current cell and update the grid
    count = countAdjacentBugs(gameGrid, bugs, column, row)
    gameGrid[(column, row)]["revealed"] = True
    
    # If the current cell has no adjacent bugs, recursively reveal adjacent cells
    if count == 0:
        for x in range(max(0, column - 1), min(COLUMNS, column + 2)):
            for y in range(max(0, row - 1), min(ROWS, row + 2)):
                revealAdjacentCells(gameGrid, bugs, x, y, COLUMNS, ROWS)
    
    return gameGrid



def handleClick(gameGrid, bugs, column, row, COLUMNS, ROWS):
    global game_over, win_state
    # Check if the clicked cell is already revealed or flagged
    if gameGrid[(column, row)].get("revealed") or gameGrid[(column, row)].get("flagged"):
        return

    # Check if the clicked cell is bugged, and reveal it if so
    if (column, row) in bugs:
        gameGrid[(column, row)]["revealed"] = True
        gameGrid[(column, row)]["bug"] = True
        

        # Game over condition: reveal all other bugs and disable further clicks
        for column, row in bugs:
            gameGrid[(column, row)]["revealed"] = True
            gameGrid[(column, row)]["bug"] = True
            
        game_over = True
        drawGrid(gameGrid, gameboyscreen)
        return

    # Otherwise, reveal the clicked cell and update the game grid
    revealAdjacentCells(gameGrid, bugs, column, row, COLUMNS, ROWS)
    # Check if all bugs are flagged correctly and all non-bug cells are revealed

    drawGrid(gameGrid, gameboyscreen)

# Game Loop
# Initialize the game grid
# gameGrid = initializeGrid(COLUMNS, ROWS)

# Initialize the flagged cell count
flagged_count = 0
# Function to reset the game
def resetGame():
    global gameGrid, bugs, flagged_count, game_over, win_state
    flagged_count = 0
    game_over = False
    win_state = False

    gameGrid = initializeGrid(COLUMNS, ROWS)
    bugs = dropBugs(BUGS, COLUMNS, ROWS, gameGrid)
    
    drawGrid(gameGrid, gameboyscreen)

def checkWinCondition(gameGrid, bugs):
    for column, row in gameGrid.keys():
        cell = gameGrid[(column, row)]
        if not cell["bug"] and not cell["revealed"]:
            return False
        if cell["bug"] and not cell["flagged"]:
            return False
    
    # Check if all non-bug cells are revealed
    for column, row in gameGrid.keys():
        cell = gameGrid[(column, row)]
        if not cell["bug"] and not cell["revealed"]:
            return False

    return True


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
  
        if game_over:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if RESET_BUTTON_POSITION[0] <= x <= RESET_BUTTON_POSITION[0] + RESET_BUTTON_SIZE[0] and RESET_BUTTON_POSITION[1] <= y <= RESET_BUTTON_POSITION[1] + RESET_BUTTON_SIZE[1]:
                    # Reset button clicked - reset the game
                    resetGame()
                    game_over = False  # Reset the game_over flag

        elif event.type == MOUSEBUTTONDOWN and not game_over:
            x, y = event.pos
            column = (x - GAME_AREA_POSITION[0]) // CELLSIZE
            row = (y - GAME_AREA_POSITION[1]) // CELLSIZE
           
            # Check if the click is within the valid grid range
            if 0 <= column < COLUMNS and 0 <= row < ROWS:
                if event.button == 1:
                    # Left mouse button clicked - reveal cell
                    handleClick(gameGrid, bugs, column, row, COLUMNS, ROWS)
                elif event.button == 3:
                    # Right mouse button clicked - flag/unflag cell
                    cell = gameGrid[(column, row)]
                    if not cell.get("revealed"):
                        # Toggle the flagged state of the cell
                        cell["flagged"] = not cell.get("flagged")
                        # Update the flagged cell count
                        if cell["flagged"]:
                            flagged_count += 1
                        else:
                            flagged_count -= 1
                        drawGrid(gameGrid, gameboyscreen)  # Update the grid after flagging/unflagging     
            
             
            elif event.button == 1 and RESET_BUTTON_POSITION[0] <= x <= RESET_BUTTON_POSITION[0] + RESET_BUTTON_SIZE[0] and RESET_BUTTON_POSITION[1] <= y <= RESET_BUTTON_POSITION[1] + RESET_BUTTON_SIZE[1]:
                # Reset button clicked - reset the game
                resetGame()
    
        # Check win condition
    if checkWinCondition(gameGrid, bugs) and not game_over:
        win_state = True
        game_over = True

    # Draw the game area and the menu
    screen.blit(background, (0, 0))
    screen.blit(gameboyscreen, GAME_AREA_POSITION)
    screen.blit(menu, MENU_AREA_POSITION)



    # Draw the reset button
    pygame.draw.rect(screen, RESET_BUTTON_COLOR, (RESET_BUTTON_POSITION, RESET_BUTTON_SIZE))
    reset_text = FONT.render("Reset", True, pygame.Color(LIGHTEST))
    reset_text_rect = reset_text.get_rect(center=(RESET_BUTTON_POSITION[0] + RESET_BUTTON_SIZE[0] // 2, RESET_BUTTON_POSITION[1] + RESET_BUTTON_SIZE[1] // 2))
    screen.blit(reset_text, reset_text_rect)
    
     # Display the flagged cell count

    flagged_text = FONT.render("Bugs: " + str(BUGS), True, pygame.Color(LIGHTEST))
    screen.blit(flagged_text, (MENU_AREA_POSITION[0] + 10, MENU_AREA_POSITION[1] + 10))

    flagged_text = FONT.render("Found: " + str(flagged_count), True, pygame.Color(LIGHTEST))
    screen.blit(flagged_text, (MENU_AREA_POSITION[0] + 10, MENU_AREA_POSITION[1] + 40))

    gameinfo_text = FONT.render("Clear all blocks and flag the bugs! ", True, pygame.Color(LIGHTEST))
    screen.blit(gameinfo_text, (MENU_AREA_POSITION[0] + 380, MENU_AREA_POSITION[1] + 25))

    if win_state:
        # Display the win message
        pygame.draw.rect(screen, WIN_MESSAGE_BG_COLOR, (WIN_MESSAGE_POSITION, WIN_MESSAGE_SIZE))
        win_message = FONT.render("Congrats, all bugs found!", True, pygame.Color(LIGHTEST))
        win_message_rect = win_message.get_rect(center=(WIN_MESSAGE_POSITION[0] + WIN_MESSAGE_SIZE[0] // 2, WIN_MESSAGE_POSITION[1] + WIN_MESSAGE_SIZE[1] // 2))
        screen.blit(win_message, win_message_rect)  

    # Update the display
    pygame.display.update()

    
    clock.tick(FPS)


