# Not Magnus
WIP classical chess engine

11/7/21 v1.2
> Introduced move ordering for the alpha-beta negamax, improved search depth from 4 to 5. Some odd moves are being played from the increase, and search time in the middlegame could be improved.
>
> To support the key function in the sort(), had to change board to a glbal variable rather than a local one in the driver.

11/6/21 v1.1.2
> Changed transposition table to use the built-in zobrist hashes as keys instead of string epd representations of the board.
>
> Optimized evaluation function by removing reliance on iterating over entire board multiple times per call. Improved search depth from 3 to 4.

11/5/21 v1.1
> Implemented a transposition table, and cleaned up the code for search algorithim while I was at it; now much more readable.
>
> Removed child board generation and just used make/unmake moves. Identified some other speed bottlenecks that I will attempt to get resolved in a future update.
>
> For some reason it will occasionally throw away pieces. Need to take a look at the evaluation algorithim.

10/27/21 v1.0.1
> Changed the alpha-beta minimax function to an alpha-beta negamax. Preparing to implement a transposition table.

10/12/21 v1.0
> Implements a simple search with alpha-beta minimax and uses an evaluation function that utilizes material eval, piece-squares tables, and tapered eval.
Optimizations need to be done and there are a few known issues. Uses codekiddy2's [opening book](https://sourceforge.net/projects/codekiddy-chess/files/Books/Polyglot%20books/Update1/). To run, download and save as `Book.bin`, or turn off opening book usage by setting `OPENING` to `False`.
> 
> Plays poorly (I can beat it).
