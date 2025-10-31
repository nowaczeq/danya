import chess
import random
import requests
import sys

def gameplay_loop():
        board = chess.Board()
        print("Welcome to danya. The engine currently makes best moves according to Stockfish 10. You are playing white.")

        pretty_print_board(board)
    
        while True:
            move = perform_player_move(board)
            board.push(move)
            pretty_print_board(board)

            if board.is_game_over():
                announce_results(board)
                break

            # DANYA'S TURN
            move = engine_move(board)
            print(f"danya played {board.san(move)}.")
            board.push(move)
            pretty_print_board(board)
            if board.is_game_over():
                announce_results(board)
                break

def pretty_print_board(ascii_board):
    ascii_board = str(ascii_board)

    piece_to_emoji = {
    "R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "P": "♟",
    "r": "♖", "n": "♘", "b": "♗", "q": "♕", "k": "♔", "p": "♙",
    ".": "·"  # dot for empty squares
    }
    
    for letter, emoji in piece_to_emoji.items():
        ascii_board = ascii_board.replace(letter, emoji)

    print(ascii_board)


def engine_move(board):
    # Random move
    # move = random.choice(list(board.legal_moves))
    # return move

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

def perform_player_move(board):
    print("Your turn.")
    while True:
        user_move = input("Input your move in algebraic notation: ")
        try:
            move = board.parse_san(user_move)
        except ValueError:
            print("Move not recognised as valid SAN format. Please try again.")
            continue

        if move not in board.legal_moves: 
            print("Move is illegal. Try again.")
            continue
        else:
            break
    
    print(f"You played {user_move}.")
    return move
    
def announce_results(board):
    print("Game is over.")
    if board.result() == "1-0":
        print("You win!")
    elif board.result() == "0-1":
        print("Morph-e wins!")
    else:
        print("Draw!")




if __name__ == "__main__":
    gameplay_loop()
