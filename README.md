# Reversi-AI

Welcome to my game-playing AI project! 

Here, I showcase the code and thought process behind my AI agent, based on an Iterative-Deepening Alpha-Beta Pruning tree search.

The agent uses an evaluation function based on a weighted sum of heuristic values. 
(A heuristic is a simple method used to evaluate the “goodness” of a particular game state or move, when a full search of the game tree is either impossible or too costly. It gives a quick, estimate of how favorable a position is, suggesting which moves or states are most promising to explore in depth. The goal of a heuristic is to balance computational efficiency with accuracy, so that the AI can make strong moves without exhaustively searching every possible future outcome).

I tried using a genetic algorithm to optimize the weights, but in the end I manually fine-tuned them so as to not counterfit/bias against the opposing agents (see the report for more detail).
I also tried using pre-move ordering and pruning the less promising moves from the search, but this resulted in less satisfactory results due to the inaccuracy of the ordering (again, see the report for more detail).

The agent also uses game state memoization to avoid redundant computations.

In the end, the agent consistently outperformed the random agent (100% winrate across all board sizes) and the greedy gpt agent (+99% winrate across all board sizes).
Against an average human player, the expected win rate is also above 99% as I have never been able to beat it!

For more info, you can refer to the report of the project, where you'll find interesting info on the various different approaches tested that led me to this final agent.

Enjoy! :)

