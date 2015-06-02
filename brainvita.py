#!/usr/bin/python

from __future__ import print_function

def display_board(board):
  ''' Given a board as a bit-map of 33 bits, it will print
      the board on screen '''
  for i in range(33):
    if i in (0,3,27,30):
      #print a indentation for these squares
      print("      ",end="")
    hole=board%2
    if hole:
      print(" o ",end="")
    else:
      print(" . ",end="")
    if i in (2,5,12,19,26,29,32):
      print("")
    board=board>>1

def generateExtractMask(masklet):
  (first,second,third) = masklet
  mask = (1<<first) | (1<<second) | (1<<third)
  return mask

def generateCheckMaskDoublets(masklet):
  (first,second,third) = masklet
  mask1 = (1<<first) | (1<<second)
  mask2 = (1<<second) | (1<<third)
  return (mask1,mask2)

def generateMasks():
  possibleMoves = []
  topRows = [(0,1,2),(3,4,5)]
  possibleMoves.extend(topRows)
  botRows = [(27,28,29),(30,31,32)]
  possibleMoves.extend(botRows)
  lefCols = [(6,13,20),(7,14,21)]
  possibleMoves.extend(lefCols)
  rightCols = [(11,18,25),(12,19,26)]
  possibleMoves.extend(rightCols)
  centerRow1 = [(i,i+1,i+2) for i in range(6,11)]
  centerRow2 = [(i,i+1,i+2) for i in range(13,18)]
  centerRow3 = [(i,i+1,i+2) for i in range(20,25)]
  possibleMoves.extend(centerRow1)
  possibleMoves.extend(centerRow2)
  possibleMoves.extend(centerRow3)
  col = (0,3,8,15,22,27,30)
  centerCol1 = [(col[i],col[i+1],col[i+2]) for i in range(5)]
  centerCol2 = [(col[i]+1,col[i+1]+1,col[i+2]+1) for i in range(5)]
  centerCol3 = [(col[i]+2,col[i+1]+2,col[i+2]+2) for i in range(5)]
  possibleMoves.extend(centerCol1)
  possibleMoves.extend(centerCol2)
  possibleMoves.extend(centerCol3)

  extractMasks=[]
  checkMasks=[]
  for i in possibleMoves:
    extractMasks.append(generateExtractMask(i))
    checkMasks.append(generateCheckMaskDoublets(i))

  return (extractMasks, checkMasks)

def possible_move(board, extractMask, checkMasks):
  onlymaskbits = board & extractMask;
  allOnes = 0x1ffffffff
  for i in range(2):
    if (onlymaskbits | checkMasks[i]) == checkMasks[i]:
      # we have a valid move.
      boardWithoutMove = board & (~extractMask)
      afterMask = ~(checkMasks[i])
      afterMask = afterMask & extractMask
      boardAfterMove = boardWithoutMove | afterMask
      return boardAfterMove
  return 0

class BoardState:
  def __init__(self, board, level, parent):
    self.board = board
    self.mylevel = level
    self.parent = parent
    self.nextmoves = []
    self.duplicateOf = None
    self.duplicates = []

class GameContext:
  def __init__(self):
    self.beginBoard = BoardState(0x1fffeffff, 33, None)
    (self.extractMasks,self.checkMasks) = generateMasks()

  def make_move(self, currentBoard):
    for (em,cm) in zip(self.extractMasks,self.checkMasks):
      result = possible_move(currentBoard, em, cm)
      if result:
        nextBoard = BoardState(result, currentBoard)
        currentBoard.nextmoves.append()


def make_move(gameContext):
  pass

def debug_prints():
  gameContext = GameContext()
  for i in gameContext.extractMasks:
    print("---")
    display_board(i)
  for i in gameContext.checkMasks:
    print("---")
    display_board(i[0])
    print("---")
    display_board(i[1])

if __name__ == "__main__":
  debug_prints()
