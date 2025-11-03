import chess
import requests
import sys
import time
import random

# Player set to white, engine to black for now
PLAYER_COLOR = chess.WHITE
ENGINE_COLOR = chess.BLACK

class Move_Review:
    def __init__(self):
        self.eval = 0
        self.mate = False
        self.hangs = True
        self.attacks = 0
        self.attacked_value = 0
        self.score = 0.0
    def calculate_review(self):
        EVAL_BLACK_MODIFIER = 1
        EVAL_WHITE_MODIFIER = 1
        ATTACK_MODIFIER = 1
        ATTACK_VALUE_MODIFIER = 1
        MATE_MODIFIER = 1
        
        if ENGINE_COLOR == chess.BLACK:
            self.score += (self.eval * EVAL_BLACK_MODIFIER)
        else:
            self.score += (self.eval * EVAL_WHITE_MODIFIER)
        if self.mate:
            self.score += MATE_MODIFIER
        self.score += (self.attacks * ATTACK_MODIFIER)
        self.score += (self.attacked_value * ATTACK_VALUE_MODIFIER)
        self.score *= (random.randrange(9, 11) / 10)

def engine_move(board):

    move_uci = MAIA(board)
    move = board.parse_uci(move_uci)
    return move

def MAIA(board):
    # Mate, Attackers, Integer Evaluation, and Aggression
    start = time.time()
    print("MAIA system initialised at 0.0")
    candidate_moves = list(board.legal_moves)
    rating_map = {}
    len_moves = len(candidate_moves)

    for i, c in enumerate(candidate_moves):
        move_str = c.uci()
        review = Move_Review()
        if is_hanging(board, move_str, attack=False):
            rating_map[move_str] = float('-inf')
            continue
        ENDPOINT = "https://stockfish.online/api/s/v2.php"
        review.eval, review.mate = get_eval_and_mate(board, c, ENDPOINT)
        print(f"{i + 1}/{len_moves}: evaluation and forced mate calculated in ", time.time() - start)
        review.attacks, review.attacked_value = analyse_attacks(board, c)
        review.calculate_review()
        rating_map[move_str] = review.score
        print(f"{i + 1}/{len_moves}: evaluation complete in ", time.time() - start)
    
    
    print("MAIA system analysis complete in ", time.time() - start)

    # TEMPORARY: FOR SHOWCASING SCORES
    sorted_keys = sorted(rating_map, key=rating_map.get)
    for key in sorted_keys:
        print(f"{key} received a score of {rating_map[key]}")
    
    return max(rating_map, key=rating_map.get)

def ANNA(board):
    # Automatic Neural Network Advancement
    pass #TODO
    return True

def is_hanging(board, move_str: str, attack: bool) -> bool:
    """
    Check whether a piece is hanging.

    Args:
        board (chess.Board): The playing board.
        move_str (str): The move written in UCI notation.
        attack (bool): Set to true if the engine checks an enemy piece, false if a friendly piece

    Returns:
        float: The area of the rectangle.
    """
    test_board = board.copy()
    move = test_board.peek()
    square = move.to_square

    if attack:
        attacking_color = ENGINE_COLOR
        defending_color = PLAYER_COLOR
    else:
        attacking_color = PLAYER_COLOR
        defending_color = ENGINE_COLOR

    attackers = test_board.attackers(attacking_color, square)
    defenders = test_board.attackers(defending_color, square)

    return (len(attackers) > 1 and not defenders)

def analyse_attacks(board, move):
    value_map = {
        "p": 1,
        "n": 3,
        "b": 3.5,
        "r": 5,
        "q": 9,
        "k": 0
    }
    test_board = board.copy()
    test_board.push(move)

    total_attacks = 0
    total_attacked_value = 0

    if is_hanging(test_board, move.uci(), True):
        # Prioritise capturing hanging pieces
        total_attacked_value += float('inf')
        total_attacks += 1
        return float('inf'), 1
    
    for square in chess.SQUARES:
        piece = test_board.piece_at(square)
        if not piece:
            continue
        piece_str = str(piece)
        piece_str = piece_str.lower()
        if test_board.color_at(square) == ENGINE_COLOR:
            continue
        attackers = test_board.attackers(ENGINE_COLOR, square)

        attack_count = len(attackers)
        total_attacks += attack_count
        
        if attack_count > 0 and piece:
            total_attacked_value  += value_map[piece_str]

    return total_attacks, total_attacked_value

def get_eval_and_mate(board, move, endpoint: str):
    test_board = board.copy()
    test_board.push(move)
    data = {
        "depth" : 10,
        "fen" : board.fen()
    }
    response = requests.get(endpoint, params = data).json()
    eval = response['evaluation']
    mate = response['mate']

    if eval:
        return int(eval), mate
    else:
        return 0, mate

if __name__ == "__main__":
    board = chess.Board()
    move = board.parse_san("e4")
    board.push(move)
    engine_move(board)