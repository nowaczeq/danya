import chess
import requests
import sys
import time
import random
from tactics import is_hanging

# Player set to white, engine to black for now
PLAYER_COLOR = chess.WHITE
ENGINE_COLOR = chess.BLACK

class Move_Review:
    def __init__(self):
        self.eval = 0
        self.hangs = False
        self.is_capture = False
        self.mobility = 0
        self.attacks = 0
        self.material_imbalance = 0
        self.attacked_value = 0
        self.black_value = 0
        self.white_value = 0
        self.openness = 0
        self.king_attackers = 0
        self.style = 0
        self.score = 0.0

    def calculate_review(self):
        STYLE_MODIFIER = 0.6
        EVAL_MODIFIER = 1
        if self.hangs:
            self.score = float('-inf')
            return

        if ENGINE_COLOR == chess.BLACK:
            self.material_imbalance += abs(self.black_value - self.white_value)
        else:
            self.material_imbalance += abs(self.white_value - self.black_value)

        self.style = (
            0.5 * self.material_imbalance +
            0.3 * self.mobility +
            0.5 * self.attacks + 
            0.5 * self.attacked_value +
            0.5 * self.openness + 
            0.5 * self.king_attackers
        )

        if self.is_capture: self.style += 1

        self.score = (self.eval * EVAL_MODIFIER) + (self.style * STYLE_MODIFIER)

def engine_move(board):

    print("player played ", board.peek())
    move_uci = MAIA(board)
    print("danya played ", move_uci)
    move = board.parse_uci(move_uci)
    return move

def MAIA(board):
    # Mate, Attackers, Integer Evaluation, and Aggression
    start = time.time()
    print("MAIA system initialised at 0.0")
    candidate_moves = list(board.legal_moves)
    rating_map = {}
    len_moves = len(candidate_moves)

    ENDPOINT = "https://stockfish.online/api/s/v2.php"
    initial_eval = get_eval_and_mate(board, None, ENDPOINT, None)
    print("Stockfish initial analysis ", initial_eval[0])

    for i, c in enumerate(candidate_moves):
        move_str = c.uci()
        review = Move_Review()

        review.hangs = is_hanging(board, c.to_square, ENGINE_COLOR)
        review.eval, bestmove = get_eval_and_mate(board, c, endpoint=ENDPOINT, bestmove=initial_eval[1])

        # Immediately disqualify moves that worsen the position
        # EVAL_MARGIN is the margin of allowed variance from the initial evaluation
        EVAL_MARGIN = 2
        if initial_eval[0] > review.eval + EVAL_MARGIN:
            print(f"{move_str} disqualified for worsening the position")
            continue
        print(f"{i + 1}/{len_moves}: evaluation and forced mate calculated in ", time.time() - start)


        values = calculate_total_value(board, c)
        review.white_value = values["white"]
        review.black_value = values["black"]
        print(f"{move_str} evaluated at {review.eval} ")

        analyse_attacks_and_mobility(board, c, review)
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


def analyse_attacks_and_mobility(board, move, review: Move_Review):

    total_attacks = 0
    total_attacked_value = 0
    
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

    # Mobility defined as the number of legal moves
    # Openness defined as the absence of pawns
    mobility = test_board.legal_moves.count()
    openness = 16 - len([p for p in test_board.piece_map().values() if p.piece_type == chess.PAWN])


    enemy_king_square = board.king(PLAYER_COLOR)
    king_attackers = board.attackers(ENGINE_COLOR, enemy_king_square)

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

    review.attacked_value = total_attacked_value
    review.attacks = total_attacks
    review.mobility = mobility
    review.openness = openness
    review.king_attackers = len(king_attackers)

    return review

def get_eval_and_mate(board, move, endpoint: str, bestmove=None):
    test_board = board.copy()
    if move != None:
        test_board.push(move)

    # Initialise eval to -inf to assume the move is dogshit
    eval = float("-inf")

    data = {
        "depth" : 10,
        "fen" : test_board.fen()
    }
    while True:
        try:
            response = requests.get(endpoint, params = data).json()
            if not response['success']:
                print("Evaluation encountered an error. Retrying...")
            else:
                break
        except Exception as e:
            print(f"Exception encountered: {e}. Retrying...")

    if response["mate"]:
        # Check who is checkmating
        engine_checkmating = (int(response["mate"]) > 0 and ENGINE_COLOR == chess.WHITE) or (int(response["mate"]) < 0 and ENGINE_COLOR == chess.BLACK)
        # Bestmove clause eliminates this if statement from firing on initial evaluations
        if engine_checkmating and bestmove:
            if move.uci() == bestmove:
                # Account for lack of evaluation during forced mates
                eval = float("inf")
                return eval, None
            else:
                # Means there is a move that is checkmating, but this is not it
                # Return -inf to allow engine to perform the best checkmating move
                eval = float("-inf")
                return eval, None
        if not engine_checkmating:
            # TODO: Configure resigning if all moves lead to being checkmated
            eval = float("-inf")
            return eval, None
    else:
        eval = int(response['evaluation'])
        # Swap sign to account negative evaluation being in Black favor
        if ENGINE_COLOR == chess.BLACK:
            eval *= -1.0
    bestmove_response = response['bestmove']
    bestmove = bestmove_response.split(' ')[1]

    return eval, bestmove
    

def calculate_total_value(board, move):
    test_board = board.copy()
    test_board.push(move)
    value_map = {
        "p": 1,
        "n": 3,
        "b": 3.5,
        "r": 5,
        "q": 9,
        "k": 0
    }
    output = {}
    output["white"] = 0
    output["black"] = 0
    for s in chess.SQUARES:
        piece = test_board.piece_at(s)
        if piece and piece.color == chess.BLACK:
            output["black"] += value_map[str(piece).lower()]
        elif piece and piece.color == chess.WHITE:
            output["white"] += value_map[str(piece).lower()]
    
    return output

def resign():
    pass

if __name__ == "__main__":
    board = chess.Board()
    move = board.parse_san("e4")
    board.push(move)
    engine_move(board)