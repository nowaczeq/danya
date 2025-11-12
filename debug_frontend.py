import tkinter as tk
from tkinter import messagebox
import chess
import engine
import random

def get_black_move(board):
    move = engine.engine_move(board)
    return move.uci()

class ChessGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("danya 1.0")

        self.board = chess.Board()
        self.square_size = 60
        self.margin = 20
        total_size = 8 * self.square_size + self.margin

        self.canvas = tk.Canvas(master, width=total_size, height=total_size)
        self.canvas.pack()

        self.draw_board()
        self.master.after(500, self.make_white_move)  # White starts automatically

    def draw_board(self):
        self.canvas.delete("all")

        for rank in range(8):
            for file in range(8):
                x1 = file * self.square_size
                y1 = (7 - rank) * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = "#EEEED2" if (rank + file) % 2 == 0 else "#769656"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if piece:
                    self.canvas.create_text(
                        x1 + self.square_size / 2,
                        y1 + self.square_size / 2,
                        text=self.piece_unicode(piece),
                        font=("Arial", 36),
                    )

        # File letters (a–h)
        for file in range(8):
            file_letter = chr(ord("a") + file)
            x = file * self.square_size + self.square_size / 2
            y = 8 * self.square_size + self.margin / 2
            self.canvas.create_text(x, y, text=file_letter, font=("Arial", 12))

        # Rank numbers (1–8)
        for rank in range(8):
            rank_number = str(rank + 1)
            x = 8 * self.square_size + self.margin / 2
            y = (7 - rank) * self.square_size + self.square_size / 2
            self.canvas.create_text(x, y, text=rank_number, font=("Arial", 12))

    def piece_unicode(self, piece):
        symbols = {
            "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
            "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
        }
        return symbols[piece.symbol()]

    def make_white_move(self):
        """White plays a random legal move automatically."""
        if self.board.turn == chess.WHITE:
            move = random.choice(list(self.board.legal_moves))
            self.board.push(move)
            self.draw_board()

            if self.board.is_game_over():
                result = self.board.result()
                messagebox.showinfo("Game Over", f"Game Over! Result: {result}")
                with open("fen.txt", "w") as txt:
                    txt.write(f"{self.board.board_fen()}@{self.board.result()}\n")
                return

            self.master.after(500, self.make_black_move)

    def make_black_move(self):
        """Black uses the engine to play."""
        if self.board.turn == chess.BLACK:
            move_uci = get_black_move(self.board)
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
            self.draw_board()

        if self.board.is_game_over():
            result = self.board.result()
            messagebox.showinfo("Game Over", f"Game Over! Result: {result}")
        else:
            self.master.after(500, self.make_white_move)

root = tk.Tk()
gui = ChessGUI(root)
root.mainloop()
