# Reversi-AI

Welcome to my game-playing AI project! 

Here, I showcase the code behind my AI agent, based on an Iterative-Deepening Alpha-Beta Pruning tree search.

The agent uses an evaluation function based on a weighted sum of heuristic values. 
(A heuristic is a simple method used to evaluate the “goodness” of a particular game state or move, when a full search of the game tree is either impossible or too costly. It gives a quick, estimate of how favorable a position is, guiding the AI’s decision-making by suggesting which moves or states are most promising to explore in depth. The goal of a heuristic is to balance computational efficiency with accuracy, so that the AI can make strong moves without exhaustively searching every possible future outcome).

I tried using a genetic algorithm to optimize the weights, but in the end I manually fine-tuned them so as to not counterfit/bias against the opposing agents (see the report for more detail).

The agent also uses game state memoization to avoid redundant computations.

For more info, you can refer to the report of the project, where you'll find interesting info on the various different approaches I tested that led me to my final agent.

Enjoy! :)
