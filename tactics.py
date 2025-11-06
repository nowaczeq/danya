import chess
import requests
import sys
import time

# Player set to white, engine to black for now
PLAYER_COLOR = chess.WHITE
ENGINE_COLOR = chess.BLACK



def is_hanging(board, square, piece_color) -> bool:
    """
    Check whether the last move left a piece hanging.
    A piece is hanging if it is simultaneously attacked and not defended by any other piece.

    Args:
        board (chess.Board): The playing board.
        attack (bool): Set to true if the engine checks an enemy piece, false if a friendly piece

    Returns:
        bool: True if the piece is hanging, false otherwise
    """

    defending_color = piece_color
    attacking_color = not defending_color

    attackers = len(board.attackers(attacking_color, square))
    defenders = len(board.attackers(defending_color, square))

    return (attackers >= 1 and defenders == 0)



# def is_underdefended(board, square) -> bool:
#     """
#     Check whether a piece is underdefended. 
#     A piece is underdefended if it is protected by a piece of lower value than the attacker.
#     Args:
#         board (chess.Board): The playing board.
#         attack (bool): Set to true if the engine checks an enemy piece, false if a friendly piece

#     Returns:
#         bool: True if the piece is hanging, false otherwise
#     """

#     value_map = {
#         "p": 1,
#         "n": 3,
#         "b": 3.5,
#         "r": 5,
#         "q": 9,
#         "k": 0
#     }
#     attacking_color = board.piece_at(square)
#     defending_color = not attacking_color

#     attackers = board.attackers(attacking_color, square)
#     defenders = board.attackers(defending_color, square)

#     lowest_attacker_value = 0
#     highest_defender_value = 0

#     for s in attackers:
#         piece = board.piece_at(s)
#         piece = piece.lower()
#         if piece and value_map[piece] < lowest_attacker_value:
#             lowest_attacker_value = value_map[piece]
    
#     for s in defenders:
#         piece = board.piece_at(s)
#         piece = piece.lower()
#         if piece and value_map[piece] > highest_defender_value:
#             highest_defender_value = value_map[piece]
        
#         return highest_defender_value < lowest_attacker_value