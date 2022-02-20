# Not Magnus
Learner classical chess engine. The goal of this project is to first and foremost learn the principles behind chess engines, and attempt to implement the most popular algorithims in modern chess engines. While I am trying to make the engine as strong as possible, the primary concern is readability and simplicity (this engine is written in Python after all).

Uses [codekiddy2's opening book](https://sourceforge.net/projects/codekiddy-chess/files/Books/Polyglot%20books/Update1/polyglot-collection.7z/download) and the [Gaviota endgame tablebase](https://chess.cygnitec.com/tablebases/gaviota/). To run, download, unzip, and save as `Opening Book/Book.bin` and `Endgame Book/...` (all .cp4 files in one folder), or turn off book usage by setting `OPENING_BOOK`/`ENDGAME_BOOK` to `False` in `util.py`.

Search depth and playing color can also be modified in `util.py`. Change player to `"COMPUTER"` for the engine to play against itself. Other less user friendly parameters can be found outside `util.py` in the appriopate places (unfortunately still in the middle of the code).

Special note of appreciation to the Chess Programming Wiki and Jeroen Carolus for his thesis "Alpha-Beta with Sibling Prediction Pruning in Chess." I wouldn't be anywhere without their help.

------

## Current Features
- Fail soft alpha-beta negamax search
- Move ordering enhancement (with history heuristic)
- Transposition table
- MTD(f) search (in an iterative deepneing framework)
- Quiescence search
- Null move pruning
- Late move reduction
- Opening book
- Gaviota endgame tablebase
- Material score evaluation
- Piece-squares table evaluation
- Tapered evaluation
- Mobility evaluation
- Piece-specific evaluation

------

## Devlog
2/20/22 v1.8
> Rewrote the evaluation function again with the innovation of bitboards, laying the groundwork for evaluation improvements.
> 
> Implemented bonuses for passed pawns and knights on outpost squares.
> 
> Implemented penalties for pinned queens, pawns being on the same colored square as the friendly bishops, and isolated pawns.

2/19/22 v1.7.5
> Update the piece-squares tables to be one list instead of 8 nested lists. Value indices now reflect the squares they belong to.

2/17/22 v1.7.4
> Committed Disservin's changes to the transposition table. Slightly modified file to clean up deprecated code, more variable consistency, and moved the timing to the main game loop to display time for computer to crunch out each move.

2/10/22 v1.7.3
> Added an evaluation bonus for rooks on open files and semi-open files.
> 
> Switch to Numpy arrays for the piece-squares tables.

2/8/22 v1.7.2
> Temporarily pivoting away from parallel search due to unsuccessful attempts at both multiprocessing and multithreading. Also need to investigate whether Python dictionaries even support lockless implementations, as they seem to be by default thread safe.
> 
> Rewrote the evaluation function from the ground-up. Expected speed gains from this, but improvements are minimal. What is odd, however, is that negamax, MTD(f), and iteratively deepening MTD(f) seems to perform at the same speed at depth 4 now.
> 
> Moved piece-squares tables to a separate file for better readability.

1/17/22 v1.7.1
> Made the transposition table lockless using Robert Hyatt and Timothy Mann's XOR technique in preparation to use it as a shared hash table for the parallel search technique Lazy SMP.

12/30/21 v1.7
> Added late move reduction. Variables are adjustable, but setting the minimum depth `reduction_threshold` too low will cause issues.
> 
> Modified move ordering with history heuristic. Speed increase seems negligible, more testing required.
> 
> Discovered and fixed a bug where null move pruning will break the engine due to the null move search also performing null move pruning.

12/29/21 v1.6
> Implemented quiescence search.
> 
> Implemented null move pruning (again!). Significantly speeds up searches.
> 
> Modified the way the transposition table is cleared. Believe previous methods have been improperly clearing it too often.

12/22/21 v1.5.4
> Modified the transposition table to correctly handle null window searches. Engine struggles in quiet positions.
> 
> Move ordering now considers transposition table moves first.
> 
> Fixed a small bug in which the algorithim wasn't spotting M1 on and only on depth 4.

12/18/21 v1.5.3
> By testing with NegaC*, found out MTD(f), NegaC*, and similar null window algorithims have been buggy because the transposition table has not been coded to store null window searches properly. Temporary fix by not storing them at all.
> 
> Applied some small tweaks. Some places benefit from using a large int constant instead of infinity.

12/16/21 v1.5.2
> Small tweaks in details of some code. I've narrowed down the issue regarding MTD(f) to a couple of factors: even depths seem to give wonky results and that initial guess *affects* end result. Reading the paper on MTD(f) I was under the impression that the initial guess only affects the speed at which you get to the end result, but not the end result itself. Unsure if the algorithim is designed this way or some part of implementation is incorrect (more than likely in my negamax, as the MTD(f) pseudocode is too simple to mess up).

11/28/21 v1.5.2
> Did some experimentation with NegaC* search, no success. Efforts on aspiration search have fell flat, but did discover that MTD(f) was acting funky because of my implementation of killer heuristic, history heurisitc, and null-move pruning.

11/22/21 v1.5.1
> Likely going to give up on MTD(f) search, and further experiments with PVS have shown little success. One iteration did run, but all it did was push every single pawn two moves forward.
> 
> In lieu of this, I tried out aspiration search with an iterative deepening step instead, and success has been decent so far. Extensive testing still needs to be done, espically with the details in the iterative deepeing method and the best step size, but initial impressions shows decent speeds at depth 5 and solid move choices.

11/21/21 v1.5
> Implemented killer and history heuristics for move ordering, though had to do this with global dictionaries. Not sure how efficient so many "in" operations is.
> 
> Added null-move pruning.
> 
> MTD(f) now refuses to compute at depth 5, and will constantly blunder on depth 4.

11/18/21 v1.4.1
> A frustrating week.
> 
> Tested simplified iterative deepening without time cut-off (whereas it simply iteratively searches depth 1, 2, ..., d) to not much of a noticable difference, if any.
> 
> Tested PVS search pseudocode without much success. Will likely stick to the MTD(f) framework.
> 
> Tested quiescence search with great pain. Discovered python-chess's is_capture() behavior was different than expected, and search had difficulty detecting actual captures. When that was resolved, discovered that qsearch broke MTD(f), but not negamax, and only on even depths. Do not know why.
> 
> Evaluation function can be improved, and search speed as well. But most majorly I can not figure out why MTD(f) occasionally produces very obvious blunders negamax does not on the same positions. It was demostrated that by improving search depth from 4 to 5 on those positions the issue was resolved, so I focused on increasing search speed; but mayhaps a look into the algorithim is better as to solve those blunders while on the same depth. Besides that move ordering heuristics seems to be the only straight-forward way to increase speed now. I have heard that python-chess's legal move generation is very slow, even though it seems to use bitboards. Looking to improve that may be another avenue.

11/13/21 v1.4.1
> Added very basic mobility score evaluation, not sure how much of an effect it has.
> 
> Organized evaluation() into separate functions for better modularity.
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
