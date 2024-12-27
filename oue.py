from abc import ABC, abstractmethod
from pieces import *
import pygame

class Square :
    def __init__(self, x, y, width, height) :
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.color = 'light' if (x+y) % 2 == 0 else 'dark'
        self.occupying_piece = None
        self.coord = self.get_coord()
        self.highlight = False
        #For pygame
        self.width = width
        self.height = height
        self.abs_x = x * width
        self.abs_y = y * height
        self.abs_pos = (self.abs_x, self.abs_y)
        self.draw_color = (220, 208, 194) if self.color == 'light' else (53,53,53)
        self.highlight_color = (100,249,83) if self.color == 'light' else (0,228,10)
        self.rect = pygame.Rect(
            self.abs_x,
            self.abs_y,
            self.width,
            self.height
        )

    def get_coord(self) :
        columns = 'abcdefgh'
        return columns[self.x] + str(self.y + 1)

    def draw(self, display) :
        if self.highlight :
            pygame.draw.rect(display,self.highlight_color,self.rect)
        else :
            pygame.draw.rect(display,self.draw_color,self.rect)
        #adds the chess piece icons
        if self.occupying_piece != None :
            centering_rect = self.occupying_piece.img.get_rect()
            centering_rect.center = self.rect.center
            display.blit(self.occupying_piece.img, centering_rect.topleft)

    def __str__(self) :
        if self.occupying_piece != None :
            return self.occupying_piece.__str__()

class Board :
    def __init__(self, width, height) :
        self.width = width
        self.height = height
        self.tile_width = width // 8
        self.tile_height = height // 8
        self.selected_piece = None
        self.turn = 'white'
        self.config=[
            ['wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR']
        ]
        self.squares = self.generate_squares()
        self.setup_board()

    def generate_squares(self) :
        squares = []
        for y in range(8) :
            for x in range(8) :
                squares.append( Square(x, y, self.tile_width, self.tile_height) )
        return squares

    def get_square_from_pos(self,pos) :
        for square in self.squares :
            if (square.x,square.y) == (pos[0], pos[1]) :
                return square
            
    def get_piece_from_pos(self, pos) :
        return self.get_square_from_pos(pos).occupying_piece

    def setup_board(self) :
        for y, row in enumerate(self.config) :
            for x, piece in enumerate(row) :
                if piece != '' :
                    square = self.get_square_from_pos((x,y))
                    if piece[1] == 'R' :
                        square.occupying_piece = Rook((x,y), 'white' if piece[0] == 'w' else 'black', self)
                    elif piece[1] == 'N' :
                        square.occupying_piece = Knight((x,y), 'white' if piece[0] == 'w' else 'black', self)
                    elif piece[1] == 'B' :
                        square.occupying_piece = Bishop((x,y), 'white' if piece[0] == 'w' else 'black', self)
                    elif piece[1] == 'Q' :
                        square.occupying_piece = Queen((x,y), 'white' if piece[0] == 'w' else 'black', self)
                    elif piece[1] == 'K' :
                        square.occupying_piece = King((x,y), 'white' if piece[0] == 'w' else 'black', self)
                    elif piece[1] == 'P' :
                        square.occupying_piece = Pawn((x,y), 'white' if piece[0] == 'w' else 'black', self)
                        
    def reset_board(self) :
        for y in range(8) :
            for x in range(8) :
                self.get_square_from_pos((x,y)).occupying_piece = None
                self.turn = 'white'
                self.selected_piece = None

    def is_in_check(self, color, board_change=None): # board_change = [(x1, y1), (x2, y2)]
        output = False
        king_pos = None
        changing_piece = None
        old_square = None
        new_square = None
        new_square_old_piece = None
        if board_change is not None :
            changing_piece = self.get_piece_from_pos(board_change[0])
            old_square = self.get_square_from_pos(board_change[0])
            new_square = self.get_square_from_pos(board_change[1])
            new_square_old_piece = self.get_piece_from_pos(board_change[1])
            new_square.occupying_piece = changing_piece
            if isinstance(changing_piece, King) :
                king_pos = new_square.pos

        pieces = [
            i.occupying_piece for i in self.squares if i.occupying_piece is not None
        ]
        
        if king_pos == None :
            for piece in pieces :
                if isinstance(piece,King) and piece.color == color :
                    king_pos = piece.pos
                    
        for piece in pieces :
            if piece.color != color :
                for square in piece.attacking_squares(self) :
                    if square.pos == king_pos :
                        output = True
                        
        if board_change is not None :
            old_square.occupying_piece = changing_piece
            new_square.occupying_piece = new_square_old_piece
            
        return output

    def is_in_checkmate(self, color) :
        pieces = [
            i.occupying_piece for i in self.squares if i.occupying_piece is not None and i.occupying_piece.color == color
        ]
        if self.is_in_check(color) :
            for piece in pieces :
                if piece.get_valid_moves(self) != [] :
                    return False
            return True
        return False
        
    
    def handle_click(self,mx,my) :
        x = mx // self.tile_width
        y = my // self.tile_height
        clicked_square = self.get_square_from_pos((x,y))
        if self.selected_piece is None :
            if clicked_square.occupying_piece is not None :
                if clicked_square.occupying_piece.color == self.turn :
                    self.selected_piece = clicked_square.occupying_piece
        elif self.selected_piece.move(self,clicked_square) :
            self.turn = 'white' if self.turn == 'black' else 'black'
        elif clicked_square.occupying_piece is not None :
            if clicked_square.occupying_piece.color == self.turn :
                self.selected_piece = clicked_square.occupying_piece

    def draw(self, display) :
        if self.selected_piece is not None :
            self.get_square_from_pos(self.selected_piece.pos).highlight = True
            for square in self.selected_piece.get_valid_moves(self) :
                square.highlight = True
        for square in self.squares :
            square.draw(display)
    
    def __str__(self) :
        string = ""
        for y in range(7,-1,-1) :
            string += "| "
            for x in range(8) :
                if self.get_square_from_pos((x,y)).occupying_piece == None :
                    string += "   | "
                else :
                    string += str(self.get_square_from_pos((x,y)).__str__()) + " | "
            string+="\n"
        return string
