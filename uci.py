from sys import stdout
from threading import Thread
import chess
from search import *
import util

def main():
    stack = []
    out = stdout
    stop_threads = False
    
    def output(s):
        out.write(str(s+"\n"))
        out.flush()
    
    while True:
        if stack:
            command = stack.pop()
        else:
            command = input()
        
        if command == "quit":
            break
        elif command == "stop":
            stop_threads = True
        elif command == "uci":
            output('id name not-magnus')
            output('id auther Devin Zhang')
            output('')
            output('option name openingbook type check default false')
            output('option name tablebase type check default false')
            output('uciok')
        elif command == "isready":
            output('readyok')
        elif command == "ucinewgame":
            board = chess.Board()
            fen = board.fen()
        elif command.startswith('position'):
            stop_threads = False
            parameters = command.split(' ')
            fen_or_startpos = parameters[1]
            index_moves = command.find('moves')
            try:
                if fen_or_startpos == 'fen':
                    board = chess.Board()
                    index_fen = command.find('fen')
                    fen = command[(index_fen+4):index_moves]
                    board.set_fen(fen)
                elif fen_or_startpos == 'startpos':
                    board = chess.Board()
                else:
                    output('Invalid position command')
                
                if 'moves' in parameters:
                    moveslist = command[index_moves:].split()[1:]
                    for move in moveslist:
                        board.push_uci(move)
                    
            except UnboundLocalError:
                output('Error: No board initialized')
        elif command.startswith('go'):
            parameters = command.split(' ')
            depth = 255
            stop_threads = False
            movetime = float('inf')
            if 'infinite' in parameters:
                pass
            elif 'depth' in parameters:
                depth = int(parameters[2])
            elif 'movetime' in parameters:
                movetime = int(parameters[2])
            elif 'nodes' in parameters:
                nodes = int(parameters[2])
            elif 'wtime' in parameters:
                index_time = parameters.index('wtime')
                wtime = int(parameters[index_time+1])
            elif 'btime' in parameters:
                index_time = parameters.index('btime')
                btime = int(parameters[index_time+1]) 
            elif 'winc' in parameters:
                index_inc = parameters.index('winc')
                winc = int(parameters[index_time+1])
            elif 'binc' in parameters:
                index_inc = parameters.index('binc')
                binc = int(parameters[index_time+1])
            else:
                depth = 255
            try:
                thread_main = Thread(target=cpu_move,args = (board, depth, movetime, lambda: stop_threads))
                thread_main.start()
            except UnboundLocalError:
                output('Error: No board initialized')
                
            
            
            
            
if __name__ == "__main__":
    main()