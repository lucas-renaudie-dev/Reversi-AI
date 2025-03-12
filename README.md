# Game-Playing AI Project

Welcome to my AI Project! In this project, I built an AI capable of playing the game Reversi, also known as Othello. 

Here, I showcase the code and thought process behind my AI agent, based on an Iterative-Deepening Alpha-Beta Pruning tree search.

The agent uses an evaluation function based on a weighted sum of heuristic values. 
(A heuristic is a simple method used to evaluate the “goodness” of a particular game state or move, when a full search of the game tree is either impossible or too costly. It gives a quick, estimate of how favorable a position is, suggesting which moves or states are most promising to explore in depth. The goal of a heuristic is to balance computational efficiency with accuracy, so that the AI can make strong moves without exhaustively searching every possible future outcome).

I tried using a genetic algorithm to optimize the weights, but in the end I manually fine-tuned them so as to not counterfit/bias against the opposing agents (see the report for more detail).
I also tried using pre-move ordering and pruning the less promising moves from the search, but this resulted in less satisfactory results due to the inaccuracy of the ordering (again, see the report for more detail).

The agent also uses game state memoization to avoid redundant computations.

In the end, the agent placed 7th out of 150 in the tournament (¤). It consistently outperformed the random agent (100% winrate across all board sizes) and the greedy gpt agent (+99% winrate across all board sizes).
Against an average human player, the expected win rate is also above 99% as I have never been able to beat it!

For more info, you can refer to the report of the project - [COMP424_Final_Project_Report.pdf](COMP424_Final_Project_Report.pdf), where you'll find much more detail on the code behind the agent, as well as info on the various different approaches tested that led to this final agent. 
If you want to look at the code directly, go to [student_agent.py](student_agent.py). If you want to read the project instructions, go to [COMP424_Final_Project.pdf](COMP424_Final_Project.pdf). 

Finally, if you'd like to test out the agent yourself, head over to https://github.com/dmeger/COMP424-Fall2024 - you'll find everything you need to know regarding the setup of the game. If you encounter any issues, try following the steps listed in [Setup.md](Setup.md).
(Note: once you are set up, you'll need to replace the given student_agent.py starter code with my student_agent.py code).

(¤): See the [final_tournament_results.xlsx](final_tournament_results.xlsx) excel sheet - my student ID is 261045005.
