# Not Magnus
WIP classical chess engine.

Uses [codekiddy2's opening book](https://sourceforge.net/projects/codekiddy-chess/files/Books/Polyglot%20books/Update1/) and the [Gaviota endgame tablebase](https://chess.cygnitec.com/tablebases/gaviota/). To run, download and save as `Opening Book/Book.bin` and `Endgame Book/...`, or turn off opening book usage by setting `OPENING_BOOK` or `ENDGAME_BOOK` to `False` in `util.py`, respectively.

Current features:
- Alpha-beta negamax search
- Move ordering enhancement
- Transposition table
- MTD(f) search
- Opening book
- Gaviota endgame tablebase
- Material score evaluation
- Piece-squares table evaluation
- Tapered evaluation
- Mobility score

11/13/21 v1.4.1
> Added very basic mobility score evaluation, not sure how much of an effect it has.
> 
> Organized evaluation() into separate functions for better modularity.
> 
> Fixed a small bug. Gaviota evaluation will now take over at the proper time when there are 7 pieces on the board (5 pieces + 2 kings) instead of 5 pieces on the board.
> 
> After some testing, it seems the blunders I've been seeing in games have been caused by the MTD(f) search. Unsure whether this is because I do can not get iterative deepening to work, whether it lacks quiescence search, lack of depth, or some other reasoning. Considering switching over to PVS.

11/12/21 v1.4
> Search will now look at the Gaviota endgame tablebase (5-men). 
>
> Turned board back into a local variable.

11/10/21 v1.3.1
> GUI will now flip board if playing as black.
> 
> After testing, engine seems comparable to my skill level (~1050 elo). It is not very strong in the endgame, and will occasionally begin a trade of pieces but forget to take back. This can likely be addressed with quiescence search.

11/8/21 v1.3
> Implemented MTD(f), but was not able to get iterative deepening to work. Searches at depth 4 and below are now wicked fast.

11/7/21 v1.2
> Introduced move ordering for the alpha-beta negamax, greatly improving speed. Could play at depth 5, though time is just slightly too long to be bearable, especially in the middlegame.
>
> To support the key function in the sort(), had to change board to a glbal variable rather than a local one in the driver.
> 
> Now clears the transposition table after each pawn move.
> 
> Preparing to implement iterative deepending and MTD(f) search.

11/6/21 v1.1.1
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
Optimizations need to be done and there are a few known issues.
> 
> Plays poorly (I can beat it).
