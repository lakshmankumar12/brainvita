#!/usr/bin/python

from __future__ import print_function
import sys
import logging

def display_board(board, screenPrint=0, moved=-1):
  ''' Given a board as a bit-map of 33 bits, it will return a string
      of the board. This can be printed or logged '''
  op=""
  for i in range(33):
    if i in (0,3,27,30):
      #print a indentation for these squares
      op+="      "
    hole=board%2
    if hole:
      if moved == i:
        op+="  x"
      else:
        op+="  o"
    else:
      op+="  ."
    if i in (2,5,12,19,26,29,32):
      op+="\n"
    board=board>>1
  if screenPrint:
    print(op)
  return op

def generateExtractMask(masklet):
  ''' Extract mask is a bit-field contains bits of positions of interest
      Its just a number.

      This function returns a EM given the trio of positions'''
  (first,second,third) = masklet
  mask = (1<<first) | (1<<second) | (1<<third)
  return mask

def generateCheckMaskDoublets(masklet):
  ''' Check mask is a bit-field contains bits of start positions of interest
      Since for a given triplet there are 2 possible moves, its a tuple of
      2 numbers

      To aid in knowing which marble moved, in every check-mask we also
      have the moving marble. Thus the check-mask is a tuple of the
      actual integer mask and the moving marble number. Further, there
      are 2 such masks'''
  (first,second,third) = masklet
  mask1 = (1<<first) | (1<<second)
  mask2 = (1<<second) | (1<<third)
  return ((mask1,third),(mask2,first))

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
  onlymaskbits = board.board & extractMask;
  for i in range(2):
    if (onlymaskbits ^ checkMasks[i][0]) == 0:
      # we have a valid move.
      boardWithoutMove = board.board & (~extractMask)
      afterMask = ~(checkMasks[i][0])
      afterMask = afterMask & extractMask
      boardAfterMove = boardWithoutMove | afterMask
      return (boardAfterMove,checkMasks[i][1])
  logging.debug("failed")
  return (0,0)

class BoardState:
  boardsCreated = 0

  def __init__(self, board, parent, moved_marble):
    self.board = board
    self.parent = parent
    if parent:
      self.mylevel = parent.mylevel - 1
    else:
      self.mylevel = 32
    self.duplicateOf = None
    self.duplicates = []
    BoardState.boardsCreated += 1
    self.moved_marble = moved_marble
    if self.mylevel > 24:
      print("Creating %d th board at level:%d"%(BoardState.boardsCreated,self.mylevel))
    if BoardState.boardsCreated % 1000000 == 0:
      print("Created %dM boards so far.. level:%d"%(BoardState.boardsCreated/1000000,self.mylevel))

def print_parent_trail(board):
  display_board(board.board,1,board.moved_marble)
  if board.parent:
    if len(board.duplicates):
      print("There are %d duplicates for this move"%len(board.duplicates))
    print_parent_trail(board.parent)

class GameContext:
  def __init__(self):
    self.beginBoard = BoardState(0x1fffeffff, None, -1)
    (self.extractMasks,self.checkMasks) = generateMasks()
    self.allStatesAtLevel = []
    for i in range(32):
      self.allStatesAtLevel.append({})

  def make_move(self, currentBoard):
    if currentBoard.mylevel == 1:
      print("Ahoy! we have a winning move")
      print_parent_trail(currentBoard)
      sys.exit(0)
    logging.debug("Entering with %d and board of:%x\n%s"%(currentBoard.mylevel, currentBoard.board, display_board(currentBoard.board,0,currentBoard.moved_marble)))
    atleast_one_next_move = 0
    for (em,cm) in zip(self.extractMasks,self.checkMasks):
      logging.debug("Trying with em of %x and checkMasks:%x and %x"%(em,cm[0][0],cm[1][0]))
      result_board,result_marble = possible_move(currentBoard, em, cm)
      if result_board:
        atleast_one_next_move = 1
        nextBoard = BoardState(result_board, currentBoard, result_marble)
        if result_board in self.allStatesAtLevel[nextBoard.mylevel]:
          logging.debug("Resulting Board %x is a duplicate"%result_board)
          duplicate = self.allStatesAtLevel[nextBoard.mylevel][result_board]
          duplicate.duplicates.append(nextBoard)
          nextBoard.duplicateOf = duplicate
          return
        self.allStatesAtLevel[nextBoard.mylevel][result_board] = nextBoard;
        self.make_move(nextBoard)
    if not atleast_one_next_move:
      logging.debug("There are no possible moves for this board")

logging.basicConfig(filename="brainvita.log",level=logging.INFO,mode="w")

gameContext = GameContext()

def debug_prints():
  for i in gameContext.extractMasks:
    print("---")
    display_board(i,1)
  for i in gameContext.checkMasks:
    print("---")
    display_board(i[0],1)
    print("---")
    display_board(i[1],1)

if __name__ == "__main__":
  #debug_prints()
  gameContext.make_move(gameContext.beginBoard)
