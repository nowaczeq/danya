import tkinter as tk
from tkinter import messagebox
import chess
import engine

def get_black_move(board):
    move = engine.engine_move(board)
    return move.uci()

class ChessGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess — You (White) vs. danya (Black)")

        self.board = chess.Board()
        self.selected_square = None

        self.square_size = 60
        board_pixels = 8 * self.square_size

        # Add margin space for rank/file labels
        self.margin = 20
        total_size = board_pixels + self.margin

        self.canvas = tk.Canvas(master, width=total_size, height=total_size)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")

        for rank in range(8):
            for file in range(8):
                x1 = file * self.square_size
                y1 = (7 - rank) * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                # Board colors
                color = "#EEEED2" if (rank + file) % 2 == 0 else "#769656"
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color
                )

                # Draw pieces
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if piece:
                    self.canvas.create_text(
                        x1 + self.square_size / 2,
                        y1 + self.square_size / 2,
                        text=self.piece_unicode(piece),
                        font=("Arial", 36),
                    )

        # Draw file letters (a–h)
        for file in range(8):
            file_letter = chr(ord("a") + file)
            x = file * self.square_size + self.square_size / 2
            y = 8 * self.square_size + self.margin / 2
            self.canvas.create_text(x, y, text=file_letter, font=("Arial", 12))

        # Draw rank numbers (1–8)
        for rank in range(8):
            rank_number = str(rank + 1)
            x = 8 * self.square_size + self.margin / 2
            y = (7 - rank) * self.square_size + self.square_size / 2
            self.canvas.create_text(x, y, text=rank_number, font=("Arial", 12))

        # Highlight selected square
        if self.selected_square is not None:
            file = chess.square_file(self.selected_square)
            rank = chess.square_rank(self.selected_square)
            x1 = file * self.square_size
            y1 = (7 - rank) * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)

    def piece_unicode(self, piece):
        symbols = {
            "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
            "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
        }
        return symbols[piece.symbol()]

    def on_click(self, event):
        if self.board.turn == chess.BLACK:
            return  # disable user input when it's Black's turn

        # Ignore clicks outside the 8x8 grid
        if event.x > 8 * self.square_size or event.y > 8 * self.square_size:
            return

        file = event.x // self.square_size
        rank = 7 - (event.y // self.square_size)
        square = chess.square(file, rank)

        if self.selected_square is None:
            # Select a White piece only
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.draw_board()

                if not self.board.is_game_over():
                    self.master.after(500, self.make_black_move)
            else:
                self.selected_square = None

        self.draw_board()

    def make_black_move(self):
        """Automatically make a move for Black."""
        if self.board.turn == chess.BLACK:
            move_uci = get_black_move(self.board)
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
            self.draw_board()

        if self.board.is_game_over():
            result = self.board.result()
            messagebox.showinfo("Game Over", f"Game Over! Result: {result}")

root = tk.Tk()
gui = ChessGUI(root)
root.mainloop()
