# Anathema Engine
WIP classical chess engine

11/5/21 v1.1
> Implemented a transposition table, and cleaned up the code for search algorithim while I was at it; now much more readable.
> Identified some speed bottlenecks that I will attempt to get resolved in the next update.

10/27/21 v1.0.1
> Changed the alpha-beta minimax function to an alpha-beta negamax. Preparing to implement a transposition table.

10/12/21 v1.0
> Implements a simple search with alpha-beta minimax and uses an evaluation function that utilizes material eval, piece-squares tables, and tapered eval.
Optimizations need to be done and there are a few known issues. Uses codekiddy2's [opening book](https://sourceforge.net/projects/codekiddy-chess/files/Books/Polyglot%20books/Update1/). To run, download and save as `Book.bin`, or turn off opening book usage by setting `OPENING` to `False`; and create `debug.txt`.
> Currently has temporary code that writes to a txt, used for debugging.
> Plays poorly (I can beat it).
