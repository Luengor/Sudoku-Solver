from ppadb.client import Client
import numpy as np
import time
import cv2

## Start ppadb client and adb
client = Client()
adb = client.devices()[0]

## Define functions
def getCapture() -> np.ndarray:
    with open('data/temp/scr.png', 'wb') as f:
        f.write(adb.screencap())
    return cv2.imread('data/temp/scr.png', cv2.IMREAD_GRAYSCALE)

def isValidState(testBoard:np.ndarray, cell:list) -> bool:
    '''
    Checks if a given board is valid only looking
    at the row, column and "box" fo the given cell
    '''
    x, y = cell
    cellValue = testBoard[y, x]
    
    row = np.where(testBoard[y, :] == cellValue)
    if len(row[0]) > 1: return False
    
    column = np.where(testBoard[:, x] == cellValue)
    if len(column[0]) > 1: return False
    
    block = np.where(testBoard[y // 3 * 3:y // 3 * 3 + 3, x // 3 * 3:x // 3 * 3 + 3] == cellValue)
    if len(block[0]) > 1: return False

    return True

def solveBoard(tBoard:np.ndarray, permIndex:int = 0) -> bool:
    '''
    Solves the sudoku on a numpy array
    Returns: bool used in the process. It will be True or False
    depending if the board is solved or not.
    '''
    x, y = permutesLoc[permIndex]
    # Go for each valid number and get deeper while its posible
    for v, val in enumerate(permutesValids[permIndex]):
        # Set the position as val
        tBoard[y, x] = val

        # If its not a valid state, skip it
        if not isValidState(tBoard, (x, y)):
            continue

        # (From now, the valid was correct)
        # If we are at the end of the chain, return True
        if permIndex == len(permutesValids) - 1:
            # print(tBoard)
            return True
        
        # If not, the recursion keeps going
        done = solveBoard(tBoard, permIndex + 1)
        
        # If that recursion was done, return True. If not, continue
        if done:
            return True
        
    # If nothing was successful, undo the board and return False
    tBoard[y, x] = 0
    return False

## Game start
# Starts the game
adb.input_tap(360, 880)
time.sleep(0.2)

# Checks if a restart is needed
cap = getCapture()
new = cv2.imread('data/new.png', cv2.IMREAD_GRAYSCALE)
if cv2.minMaxLoc(cv2.matchTemplate(cap, new, cv2.TM_CCOEFF_NORMED))[1] > 0.9:
    adb.input_tap(500, 840)
del new, cap
time.sleep(1.5)

## Pattern recognition
# Gets capture and reads numbers from disk
capture = getCapture()
ns = [cv2.imread('data/numbers/n%s.png' % x, cv2.IMREAD_GRAYSCALE) for x in range(1, 10)]

# Template match
ress = [cv2.matchTemplate(capture, n, cv2.TM_CCOEFF_NORMED) for n in ns]
threshold = 0.95
locs = [np.where(res >= threshold)[::-1] for res in ress]
del capture, ns, ress, threshold

## Create and fill board
# Create
board = np.zeros((9, 9), dtype=np.int0)
# Fill
for n, loc in enumerate(locs):
    for pos in zip(*loc):
        x = pos[0] // 80
        y = (pos[1] - 256) // 80
        board[y, x] = n + 1
del locs

## Locate and get possible permutations
permutesLoc = [[y, x] for x, y in zip(*np.where(board == 0))]
permutesValids = []
for x, y in permutesLoc:
    valids = [x for x in range(1, 10)]
    # Row check
    for n in board[y, :]:
        if n in valids:
            valids.remove(n)
    # Column check
    for n in board[:, x]:
        if n in valids:
            valids.remove(n)
    # Block check
    block = board[y // 3 * 3:y // 3 * 3 + 3, x // 3 * 3:x // 3 * 3 + 3]
    for n in block.flatten():
        if n in valids:
            valids.remove(n)
    permutesValids.append(valids)

## Solve board
unsolvedBoard = np.array(board, dtype=np.int0)
solved = solveBoard(board)
if solved:
    print('Solved!')
    print(board)
else:
    print('F :(')

## Get taps location
taps = [[] for x in range(9)]
tapsLoc = np.where((board - unsolvedBoard) != 0)
for y, x in zip(*tapsLoc):
    v = board[y, x]
    taps[v-1].append([x, y])

# Tap screen
for n, tap in enumerate(taps):
    # Number select
    x = 123 + (n % 5) * 120
    y = 1126 + (n // 5) * 120
    adb.input_tap(x, y)
    print(f'Select number {n+1}')

    # Tap numbers
    for t in tap:
        x = 80 * t[0] + 48
        y = 80 * t[1] + 256
        adb.input_tap(x, y)
        print(f'{n+1} at {x, y}')

print('Done! (hopefully)')
