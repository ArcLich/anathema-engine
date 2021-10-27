# chessai
WIP classical chess engine

10/27/21

v1.0.1 changes the alpha-beta minimax function to an alpha-beta negamax. Preparing to implement a transposition table.

10/12/21

v1.0 implements a simple search with alpha-beta minimax and uses an evaluation function that utilizes material eval, piece-squares tables, and tapered eval.
Optimizations need to be done and there are a few known issues. Uses codekiddy2's opening book (https://sourceforge.net/projects/codekiddy-chess/files/Books/Polyglot%20books/Update1/).
Currently has temporary code that writes to a txt, used for debugging.
Plays poorly (I can beat it).
