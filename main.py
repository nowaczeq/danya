import chess
import random
import requests
import sys
from engine import engine_move
 
def gameplay_loop():
        board = chess.Board()
        print("Welcome to danya. The engine currently makes best moves according to Stockfish 10. You are playing white.")

        pretty_print_board(board)
    
        while not board.is_game_over():
            move = perform_player_move(board)
            board.push(move)
            pretty_print_board(board)

            # DANYA'S TURN
            move = engine_move(board)
            print(f"danya played {board.san(move)}.")
            board.push(move)
            pretty_print_board(board)

        announce_results(board)
        return True

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
    
def announce_results(board):
    print("Game is over.")
    if board.result() == "1-0":
        print("You win!")
    elif board.result() == "0-1":
        print("danya wins!")
    else:
        print("Draw!")


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


if __name__ == "__main__":
    gameplay_loop()
