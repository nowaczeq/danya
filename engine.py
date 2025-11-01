import chess
import requests
import sys
import time

WHITE = True
BLACK = False

# Player set to white, engine to black for now
PLAYER_COLOR = WHITE
ENGINE_COLOR = BLACK

def engine_move(board):

    # Get the list of candidate moves from the legal moves

    # For each one:
    # Check whether it's checkmate after the move
    # Check whether it's forced mate
    # Get the evaluation after the move
    # Get the number of attacked pieces after the move, and the value of those pieces
    # Check whether any piece is hanging
    # Get whether it's check after the move

    move = MAIA(board)

    # Play Stockfish's best move
    print("danya's move. danya's thinking...")
    ENDPOINT = "https://stockfish.online/api/s/v2.php"
    data = {
        "depth" : 10,
        "fen" : board.fen()
    }
    response = requests.get(ENDPOINT, params=data).json()
    print("danya has his move...")
    bestmove = response['bestmove']
    print(bestmove)
    
    # Parse stockfish response, format: "bestmove [move1move2] ponder [move1move2]"
    next_moves = bestmove.split(' ')[1]
    move = board.parse_uci(next_moves)
   
    return move

def MAIA(board):
    # Mate, Attackers, Integer Evaluation, and Aggression
    start = time.time()
    print("MAIA system initialised at 0.0")
    candidate_moves = list(board.legal_moves)
    rating_map = {}
    len_moves = len(candidate_moves)

    for i, c in enumerate(candidate_moves):
        ENDPOINT = "https://stockfish.online/api/s/v2.php"
        eval, mate = get_eval_and_mate(board, c, ENDPOINT)
        print(f"{i + 1}/{len_moves}: evaluation and forced mate calculated in ", time.time() - start)
        attacks, attacked_value = analyse_attacks(board, c)
        print(f"{i + 1}/{len_moves}: evaluation complete in ", time.time() - start)
    
    print("MAIA system analysis complete in ", time.time() - start)

def ANNA(board):
    # Automatic Neural Network Advancement
    pass #TODO
    return True


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
    hanging_pieces = ()
    for square in chess.SQUARES:
        piece = test_board.piece_at(square)
        piece_str = str(piece)
        piece_str = piece_str.lower()
        if test_board.color_at(square) != ENGINE_COLOR:
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

    return int(eval), mate
