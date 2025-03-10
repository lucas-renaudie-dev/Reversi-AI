# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
import numpy as np
from copy import deepcopy
import time
from helpers import random_move, count_capture, get_directions, check_endgame, get_valid_moves

@register_agent("student_agent")
class StudentAgent(Agent):
    def __init__(self, optimized_weights=None):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.autoplay = True
        self.max_time_per_turn = 1.95 
        self.start_time = None
        self.time_limit = None
        self.killer_moves = {}
        self.history_table = {}
        self.nodes_visited_total = 0
        self.nodes_visited_for_move = 0
        self.transposition_table = {}
        self.transposition_table_keys = []
        self.transposition_table_limit = 1000000
        self.history_table_limit = 1000000
        self.positional_weights = None
        self.leaf = 0

        if optimized_weights is None:
            self.optimized_weights = self.load_optimized_weights()
        else:
            self.optimized_weights = optimized_weights
    
    def load_optimized_weights(self):
        # Define weights for early, mid, and late game phases
        return [
            # Early Game Weights (indices 0-6)
            5,   # weight_pieces (maybe change to 3)
            40,  # weight_corners
            10,  # weight_mobility (maybe change to 15)
            15,   # weight_stability
            -5,  # weight_frontier
            0,   # weight_parity
            15,  # weight_position (maybe change to 20)

            # Mid Game Weights (indices 7-13)
            10,   # weight_pieces
            60,  # weight_corners
            15,  # weight_mobility
            20,  # weight_stability
            -10, # weight_frontier
            0,   # weight_parity
            10,  # weight_position

            # Late Game Weights (indices 14-20)
            20,  # weight_pieces
            50,  # weight_corners
            5,   # weight_mobility
            30,  # weight_stability
            -15, # weight_frontier
            10,  # weight_parity (most beneficial in endgame)
            5    # weight_position
        ]
    
    def step(self, chess_board, player, opponent):
        """
        Determine the next move using IDS alpha-beta with smart move ordering
        """

        board_size = chess_board.shape[0]
        self.start_time = time.time()
        self.time_limit = self.start_time + self.max_time_per_turn

        # Reset per-move variables
        self.killer_moves = {}
        self.history_table = {}
        self.nodes_visited_total = 0
        self.leaf = 0
        self.transposition_table.clear()
        self.transposition_table_keys = []

        # Generate positional weights based on the board size 
        self.positional_weights = get_positional_weights(board_size)

        valid_moves = get_valid_moves(chess_board, player)
        if (np.count_nonzero(chess_board)==4) : 
            return (valid_moves[np.random.randint(0,4)]) # make the first move random if we are playing first
        if not valid_moves:  # Pass turn if no valid moves
            return None
        elif len(valid_moves) == 1:
            return valid_moves[0]  # Only one move

        # Start with depth 1 and increase depth iteratively
        depth = 1
        best_move = None
        max_iterative_depth = 25

        try:
            while depth <= max_iterative_depth:
                if time.time() >= self.time_limit:
                    break 
                # IDS with alpha-beta pruning
                current_best_move, current_best_score = self.alpha_beta_search(
                    chess_board, player, opponent, depth
                )
                # print(f"Depth {depth}, t={(2 - (self.time_limit - time.time())):.2f}, Best Move: {current_best_move}, Score: {current_best_score:2f}, Positions Evaluated: {self.leaf}, Minimax Calls: {self.nodes_visited_total}")
                best_move = current_best_move
                depth += 1
        except TimeoutError:
            pass 

        if best_move is None and valid_moves:  # go to the first valid move
            best_move = valid_moves[0]
        return best_move

    def alpha_beta_search(self, chess_board, player, opponent, max_depth):
        """
        Alpha-beta IDS
        """
        alpha = float('-inf')
        beta = float('inf')
        best_score = float('-inf')
        best_move = None

        valid_moves = get_valid_moves(chess_board, player)
        ordered_moves = self.order_moves(chess_board, valid_moves, player, 0)

        for move in ordered_moves:
            self.nodes_visited_for_move = 0
            if time.time() >= self.time_limit:
                raise TimeoutError 

            new_board = chess_board.copy()
            new_board = self.make_move(new_board, move, player)
            score = self.minimax(new_board, max_depth - 1, False, player, opponent, alpha, beta, 1, max_depth)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)

        return best_move, best_score

    def minimax(self, board, depth, maximizing_player, player, opponent, alpha, beta, current_depth, max_depth):
        self.nodes_visited_total += 1
        self.nodes_visited_for_move += 1

        if time.time() >= self.time_limit:
            raise TimeoutError  # Time limit exceeded

        # Terminal condition
        if depth == 0 or np.count_nonzero(board == 0) == 0:
            score = self.evaluate_board(board, player, opponent)
            # Debug print to monitor evaluation scores
            # print(f"Depth {current_depth}, Evaluated Score: {score}")
            self.leaf += 1
            return score

        board_hash = self.hash_board(board)
        if board_hash in self.transposition_table:
            stored_score, stored_depth = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return stored_score

        valid_moves = get_valid_moves(board, player if maximizing_player else opponent)

        if not valid_moves:
            # Check if the opponent also has no moves
            opponent_moves = get_valid_moves(board, opponent if maximizing_player else player)
            if not opponent_moves:
                score = self.evaluate_board(board, player, opponent)
                # print(f"Depth {current_depth}, Evaluated Score (No Moves for Both): {score}")
                return score
            else:
                # Pass turn to the opponent without decrementing depth
                return self.minimax(board, depth, not maximizing_player, player, opponent, alpha, beta, current_depth + 1, max_depth)

        if maximizing_player:
            max_eval = float('-inf')
            ordered_moves = self.order_moves(board, valid_moves, player, current_depth)
            for move in ordered_moves:
                new_board = board.copy()
                new_board = self.make_move(new_board, move, player)
                eval = self.minimax(new_board, depth - 1, False, player, opponent, alpha, beta, current_depth + 1, max_depth)
                if eval > max_eval:
                    max_eval = eval
                    self.update_history_table(move, depth)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.record_killer_move(current_depth, move)
                    break
            self.store_in_transposition_table(board_hash, max_eval, depth)
            return max_eval
        else:
            min_eval = float('inf')
            ordered_moves = self.order_moves(board, valid_moves, opponent, current_depth)
            for move in ordered_moves:
                new_board = board.copy()
                new_board = self.make_move(new_board, move, opponent)
                eval = self.minimax(new_board, depth - 1, True, player, opponent, alpha, beta, current_depth + 1, max_depth)
                if eval < min_eval:
                    min_eval = eval
                    self.update_history_table(move, depth) 
                beta = min(beta, eval)
                if beta <= alpha:
                    self.record_killer_move(current_depth, move)
                    break
            self.store_in_transposition_table(board_hash, min_eval, depth)
            return min_eval

    def make_move(self, board, move, player):
        """
        Execute the move and return the new board
        """
        flips = self.get_flipped_positions(board, move, player)
        board[move] = player
        for pos in flips:
            board[pos] = player
        return board

    def get_flipped_positions(self, board, move, player):
        """
        Get the list of positions that would be flipped if the player makes the move
        """
        opponent = 3 - player  # player values are 1 and 2
        flips = []
        board_size = board.shape[0]

        for direction in get_directions():
            dx, dy = direction
            r, c = move
            r += dx
            c += dy
            discs_to_flip = []
            while 0 <= r < board_size and 0 <= c < board_size and board[r, c] == opponent:
                discs_to_flip.append((r, c))
                r += dx
                c += dy
            if 0 <= r < board_size and 0 <= c < board_size and board[r, c] == player:
                flips.extend(discs_to_flip)
        return flips
 
    def order_moves(self, board, moves, player, current_depth):
        """
        Order moves using killer move, history heuristic, positional weights, and discs flipped
        """
        board_size = board.shape[0]
        move_scores = []

        for move in moves:
            if not (0 <= move[0] < board_size and 0 <= move[1] < board_size):
                continue  

            new_board = board.copy()
            new_board = self.make_move(new_board, move, player)

            score = 0
            # Killer move heuristic
            if move in self.killer_moves.get(current_depth, []):
                score += 1000  # prioritize killer moves
            
            # Corner heuristic
            corners = [(0, 0), (0, board_size - 1), (board_size - 1, 0), (board_size - 1, board_size - 1)]
            if move in corners:
                score += 1000

            # Stability Heuristic
            stability_score = self.calculate_stability(new_board, player)
            score += stability_score * 20  # Weight for stability in ordering

            # History heuristic
            # prioritizes moves that have been successful in improving evaluations during other searches
            # history table keeps track of these moves and assigns higher scores to frequently beneficial ones
            score += 20 *self.history_table.get(move, 0)

            # Positional weights heuristic
            positional_weight = self.positional_weights[move[0]][move[1]]
            score += positional_weight * 10 

            # Number of discs flipped heuristic
            num_discs_flipped = count_capture(board, move, player)
            score += num_discs_flipped * 5 

            move_scores.append((score, move))

        # Sort moves in descending order of their scores
        move_scores.sort(reverse=True, key=lambda x: x[0])
        ordered_moves = [move for score, move in move_scores]
        return ordered_moves

    def record_killer_move(self, depth, move):
        """
        Record a killer move for a specific depth. We keep up to 2 killer moves per depth
        """
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []

        if move not in self.killer_moves[depth]:
            if len(self.killer_moves[depth]) < 2:
                self.killer_moves[depth].append(move)
            else:
                # Replace oldest killer move
                self.killer_moves[depth][0] = self.killer_moves[depth][1]
                self.killer_moves[depth][1] = move

    def update_history_table(self, move, depth):
        """
        Update history table with the move and depth
        """
        if len(self.history_table) >= self.history_table_limit:
            # Remove an arbitrary move to keep the size under limit
            self.history_table.pop(next(iter(self.history_table)))
        self.history_table[move] = self.history_table.get(move, 0) + 2 ** depth

    def evaluate_board(self, board, player, opponent):
        """
        Evaluate the board based on game state and different heuristics
        1. pieces: Measures the difference in the number of pieces each player controls, favoring boards where the player has more pieces
        2. corners: Rewards occupying corner positions, as they are stable and cannot be flipped once captured
        3. mobility: Evaluates the player's ability to make moves compared to the opponent, prioritizing higher mobility to retain control
        4. stability: Counts discs that are unlikely/impossible to be flipped for the remainder of the game, as they contribute to a secure position
        5. frontier: Penalizes pieces on the frontier (adjacent to empty spaces), as they are more vulnerable to being flipped
        6. parity: Accounts for the parity of empty squares, favoring configurations that lead to favorable turn order in the endgame
        7. position: Rewards control of strategically valuable positions based on a weighted positional matrix
        8. potential mobility: Considers the player's ability to increase future mobility by limiting the opponent's potential moves
        """
        # Determine game phase
        weight_potential_mobility = 0
        total_discs = np.count_nonzero(board)
        board_size = board.shape[0]
        total_squares = board_size * board_size
        if total_discs <= total_squares * 0.25: # early game
            weight_index = 0
            weight_potential_mobility = 7 # (maybe change to 10)
        elif total_discs <= total_squares * 0.75: # middle game
            weight_index = 7
            weight_potential_mobility = 5
        else: # end game
            weight_index = 14
            weight_potential_mobility = 2

        # Extract weights for the current game phase
        weights = self.optimized_weights[weight_index:weight_index + 7]
        (weight_pieces, weight_corners, weight_mobility, weight_stability,
         weight_frontier, weight_parity, weight_position) = weights
        
        if (board_size == 6):
            if (weight_index <= 7):
                weight_mobility += 15
            weight_corners += 30 # corners and edges are crucial on 6x6 board
            weight_stability += 10
        elif (board_size == 8):
            # add any 8x8 specific tunings here
            pass
        elif (board_size == 10):
            weight_potential_mobility += 5 # keeping options on larger boards is more important than smaller ones
        elif (board_size ==12):
            weight_potential_mobility += 5 # keeping options on larger boards is more important than smaller ones
            weight_frontier -= 5 # penalize frontiers even more on large boards

        # Piece difference
        player_pieces = np.count_nonzero(board == player)
        opponent_pieces = np.count_nonzero(board == opponent)
        piece_diff = player_pieces - opponent_pieces

        # Corner occupancy
        corners = [(0, 0), (0, board_size - 1), (board_size - 1, 0), (board_size - 1, board_size - 1)]
        player_corners = sum(1 for corner in corners if board[corner] == player)
        opponent_corners = sum(1 for corner in corners if board[corner] == opponent)
        corner_diff = player_corners - opponent_corners

        # Mobility
        player_moves = len(get_valid_moves(board, player))
        opponent_moves = len(get_valid_moves(board, opponent))
        if player_moves + opponent_moves != 0:
            mobility = 100 * (player_moves - opponent_moves) / (player_moves + opponent_moves)
        else:
            mobility = 0

        # Frontier Discs
        player_frontier_discs = self.count_frontier_discs(board, player)
        opponent_frontier_discs = self.count_frontier_discs(board, opponent)
        frontier_diff = player_frontier_discs - opponent_frontier_discs

        # Parity
        empty_squares = total_squares - total_discs
        parity = 1 if empty_squares % 2 == 0 else -1

        # Positional score
        positional_score = np.sum(self.positional_weights * (board == player)) - \
                           np.sum(self.positional_weights * (board == opponent))

        # Potential Mobility
        potential_mobility = self.calculate_potential_mobility(board, player, opponent)

        # Stability
        stability = self.calculate_stability(board, player) - self.calculate_stability(board, opponent)

        # Total evaluation
        score = (
            weight_pieces * piece_diff +
            weight_corners * corner_diff +
            weight_mobility * mobility +
            weight_stability * stability +
            weight_frontier * frontier_diff +
            weight_parity * parity +
            weight_position * positional_score +
            weight_potential_mobility * potential_mobility
        )

        # can add forcing move heuristic here
        if opponent_moves==0:
            score += 1000 # can tune

        return score

    def count_frontier_discs(self, board, player):
        """
        Count the number of frontier discs
        """
        frontier_discs = 0
        board_size = board.shape[0]
        directions = get_directions()

        for i in range(board_size):
            for j in range(board_size):
                if board[i, j] == player:
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < board_size and 0 <= nj < board_size:
                            if board[ni, nj] == 0:
                                frontier_discs += 1
                                break  # Count each disc only once
        return frontier_discs

    def calculate_potential_mobility(self, board, player, opponent):
        """
        Calculate potential mobility for the player
        """
        potential_mobility = 0
        board_size = board.shape[0]
        directions = get_directions()

        for i in range(board_size):
            for j in range(board_size):
                if board[i, j] == 0:
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < board_size and 0 <= nj < board_size:
                            if board[ni, nj] == opponent:
                                potential_mobility += 1
                                break
        return potential_mobility

    def calculate_stability(self, board, player):
        """
        Calculate the stability of the player's discs
        """
        board_size = board.shape[0]
        stability_matrix = np.zeros((board_size, board_size), dtype=bool)
        stable_discs = 0

        # Directions
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        # Corners
        corners = [(0, 0), (0, board_size - 1), (board_size - 1, 0), (board_size - 1, board_size - 1)]

        # Check stability starting from corners
        for corner in corners:
            if board[corner] == player:
                self.mark_stable_discs(board, stability_matrix, corner, player, directions)

        stable_discs = np.count_nonzero(stability_matrix)
        return stable_discs

    def mark_stable_discs(self, board, stability_matrix, position, player, directions):
        """
        Mark stable discs starting from a given position
        """
        stack = [position]
        board_size = board.shape[0]
        while stack:
            x, y = stack.pop()
            stability_matrix[x, y] = True
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < board_size) and (0 <= ny < board_size):
                    if not stability_matrix[nx, ny] and board[nx, ny] == player:
                        stability_matrix[nx, ny] = True
                        stack.append((nx, ny))

    def hash_board(self, board):
        """
        Create hashable representation of the board
        """
        # Use an immutable representation to prevent issues with in-place modifications
        return tuple(map(tuple, board))

    def store_in_transposition_table(self, board_hash, value, depth):
        """
        Store a value in the transposition table with size limit
        """
        if board_hash in self.transposition_table:
            stored_value, stored_depth = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return  # Do not overwrite an entry with a higher or equal depth
        self.transposition_table[board_hash] = (value, depth)
        self.transposition_table_keys.append(board_hash)
        if len(self.transposition_table_keys) > self.transposition_table_limit:
            # Remove oldest item
            oldest_key = self.transposition_table_keys.pop(0)
            del self.transposition_table[oldest_key]

# Define constant matrices for different board sizes
# Explanation:
# 120 for corners as they are the highest value position
# -40 for X-sqaures (diagonally adjacent to corners) as they can give up corners AND positional control
# -20 for C-squares (adjacent to corners) because althought they can give up corners they can give stable edge positions 
# 15 for diagonally adjacent to X-squares as they can help to capture corners
# -5 for second outer ring as those can lead to losing edge squares
# 5 for edges as they can lead to stable discs (unflippable in the future)
# 3 for all the rest
# based on weights from this website
# https://reversiworld.wordpress.com/category/weighted-square-value/

POS_WEIGHTS_6x6 = np.array([
    [120, -20,  20,  20, -20, 120],
    [-20, -40,   3,   3, -40, -20],
    [ 20,   3,  15,  15,   3,  20],
    [ 20,   3,  15,  15,   3,  20],
    [-20, -40,   3,   3, -40, -20],
    [120, -20,  20,  20, -20, 120]
])

POS_WEIGHTS_8x8 = np.array([
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [ 5,   -5,   3,   3,   3,   3,  -5,  5],
    [ 5,   -5,   3,   3,   3,   3,  -5,  5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120]
])

POS_WEIGHTS_10x10 = np.array([
    [120, -20,  20,   5,   5,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,   3,   3,  15,  -5,  20],
    [ 5,   -5,   3,   3,   3,   3,   3,   3,  -5,  20],
    [ 5,   -5,   3,   3,   3,   3,   3,   3,  -5,  5],
    [ 5,   -5,   3,   3,   3,   3,   3,   3,  -5,  5],
    [ 5,   -5,   3,   3,   3,   3,   3,   3,  -5,  5],
    [ 20,  -5,  15,   3,   3,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,   5,   5,  20, -20, 120]
])

POS_WEIGHTS_12x12 = np.array([
    [120, -20,  20,   5,   5,   5,   5,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,   3,   3,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,   3,   3,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,   5,   5,   5,   5,  20, -20, 120]
])

# Dictionary to map board size to positional weights
POS_WEIGHT_MAP = {
    6: POS_WEIGHTS_6x6,
    8: POS_WEIGHTS_8x8,
    10: POS_WEIGHTS_10x10,
    12: POS_WEIGHTS_12x12
}

def get_positional_weights(board_size):
    """
    Retrieve the positional weight matrix for the given board size
    """
    if board_size in POS_WEIGHT_MAP:
        return POS_WEIGHT_MAP[board_size]
    
def print_all_matrices():
    """
    Generate and print positional weights for board sizes 6x6, 8x8, 10x10, and 12x12.
    """
    board_sizes = [6, 8, 10, 12]
    for size in board_sizes:
        print(f"Positional Weights for {size}x{size} Board:\n")
        print(np.array(get_positional_weights(size)))
        print("\n")
