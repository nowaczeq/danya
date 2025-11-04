import chess
import requests
import sys
import time
import random
from tactics import is_hanging, is_underdefended

# Player set to white, engine to black for now
PLAYER_COLOR = chess.WHITE
ENGINE_COLOR = chess.BLACK

class Move_Review:
    def __init__(self):
        self.eval = 0
        self.mate = False
        self.hangs = False
        self.is_capture = True
        self.attacks = 0
        self.attacked_value = 0
        self.score = 0.0
    def calculate_review(self):
        EVAL_BLACK_MODIFIER = 1
        EVAL_WHITE_MODIFIER = 1
        ATTACK_MODIFIER = 1
        ATTACK_VALUE_MODIFIER = 1
        MATE_MODIFIER = 1
        
        # Swap sign to account negative evaluation being in Black favor
        if ENGINE_COLOR == chess.BLACK:
            self.score -= (self.eval * EVAL_BLACK_MODIFIER)
        else:
            self.score += (self.eval * EVAL_WHITE_MODIFIER)
        if self.mate:
            self.score += MATE_MODIFIER
        
        if self.hangs:
            self.score = float('-inf')
            return
        
        if self.is_capture:
            self.score += 50.0
        
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
        review.hangs = is_hanging(board, c.to_square, ENGINE_COLOR)
        if review.hangs:
            print(f"{move_str} disqualified for hanging a piece")
            continue
        review.is_capture = board.is_capture(c)
        ENDPOINT = "https://stockfish.online/api/s/v2.php"
        review.eval, review.mate = get_eval_and_mate(board, c, ENDPOINT)
        print(f"{i + 1}/{len_moves}: evaluation and forced mate calculated in ", time.time() - start)
        review.attacks, review.attacked_value = analyse_attacks(board, c)
        if review.attacked_value == float('inf') and board.piece_at(c.to_square):
            print("Found a move that attacks a hanging piece: ", move_str)
            return move_str
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


def analyse_attacks(board, move):

    total_attacks = 0
    total_attacked_value = 0

    if is_hanging(board, move.to_square, PLAYER_COLOR):
        # Prioritise capturing hanging pieces
        total_attacked_value += float('inf')
        total_attacks += 1
        return total_attacks, total_attacked_value
    
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
    if not response['success']:
        print("Evaluation encountered an error. Retrying...")
        return get_eval_and_mate(board, move, endpoint)
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