from abc import ABC, abstractmethod
import pygame

class Piece(ABC) :
    def __init__(self, pos, color, board) :
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.color = color
        self.has_moved = False
        
    def get_moves(self, board) :
        output = []
        for direction in self.get_possible_moves(board) :
            for square in direction :
                if square.occupying_piece is not None :
                    if square.occupying_piece.color == self.color :
                        break
                    else :
                        output.append(square)
                        break
                else :
                    output.append(square)
        return output

    def get_valid_moves(self, board):
        output = []
        if self.get_moves(board) != None :
            for square in self.get_moves(board):
                if not board.is_in_check(self.color, board_change=[self.pos, square.pos]):
                    output.append(square)
        return output

    def move(self, board, square, force=False):
        for i in board.squares :
            i.highlight = False
        if square in self.get_valid_moves(board) or force :
            prev_square = board.get_square_from_pos(self.pos)
            self.pos, self.x, self.y = square.pos, square.x, square.y
            prev_square.occupying_piece = None
            square.occupying_piece = self
            board.selected_piece = None
            self.has_moved = True
            # Pawn promotion
            if isinstance(self,Pawn) :
                if self.y == 0 or self.y == 7 :
                    square.occupying_piece = Queen(
                        self.pos,
                        self.color,
                        board)
            # Move rook if king castles
            if isinstance(self,King) :
                if prev_square.x - self.x == 2 :
                    rook = board.get_piece_from_pos((0,self.y))
                    rook.move(board, board.get_square_from_pos((2, self.y)), force = True)
                elif prev_square.x - self.x == -2 :
                    rook = board.get_piece_from_pos((7, self.y))
                    rook.move(board, board.get_square_from_pos((4, self.y)), force=True)
            return True
        else :
            board.selected_piece = None
            return False

    #True for all pieces except pawn
    def attacking_squares(self, board):
        return self.get_moves(board)
    
    @abstractmethod
    def __str__(self) :
        pass

''' KING '''
class King(Piece) :
    def __init__(self, pos, color, board) :
        super().__init__(pos, color, board)
        img_path = 'img/' + color[0] + '_king.png'
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (board.tile_width - 20, board.tile_height - 20))
        self.notation = 'K'
        
    def get_possible_moves(self, board) :
        output = []
        moves = [
            (-1,-1),
            (-1,0),
            (-1,1),
            (0,-1),
            (0,1),
            (1,-1),
            (1,0),
            (1,1) ]
        for move in moves :
            new_pos = (self.x+move[0],self.y+move[1])
            if (new_pos[0] < 8
                and new_pos[0] >= 0
                and new_pos[1] < 8
                and new_pos[1] >= 0) :
                output.append([board.get_square_from_pos(new_pos)])
        return output
        
    def can_castle(self, board) :
        if not self.has_moved :
            if self.color == 'black' :
                row = 7
            elif self.color == 'white' :
                row = 0
                
            queenside_rook = board.get_piece_from_pos((0,row))
            kingside_rook = board.get_piece_from_pos((7,row))
            if queenside_rook is not None :
                if not queenside_rook.has_moved :
                    if [
                        board.get_piece_from_pos((i,row)) for i in range(4,7)
                        ] == [ None, None, None ] :
                        return 'queenside'
            if kingside_rook is not None :
                if not kingside_rook.has_moved :
                    if [
                        board.get_piece_from_pos((i,row)) for i in range(1,3)
                        ] == [ None, None ] :
                        return 'kingside'

    def get_valid_moves(self, board) :
        output = []
        for square in self.get_moves(board) :
            if not board.is_in_check(self.color, board_change=[self.pos,square.pos]) :
                output.append(square)
        if self.can_castle(board) == 'queenside' :
            output.append(
                board.get_square_from_pos((self.x + 2, self.y))
            )
        if self.can_castle(board) == 'kingside' :
            output.append(
                board.get_square_from_pos((self.x - 2, self.y))
            )
        return output
    
    def __str__(self) :
        return ('w' if self.color == 'white' else 'b')  +"K"

''' QUEEN '''
class Queen(Piece) :
    def __init__(self, pos, color, board) :
        super().__init__(pos, color, board)
        img_path = 'img/' + color[0] + '_queen.png'
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (board.tile_width - 20, board.tile_height - 20))
        self.notation = 'Q'
        self.value = 9
        
    def get_possible_moves(self, board):
        output = []
        bishop = Bishop(self.pos, self.color, board)
        rook = Rook(self.pos, self.color, board)
        for diagonal in bishop.get_possible_moves(board) :
            output.append(diagonal)
        for line in rook.get_possible_moves(board) :
            output.append(line)
        return output

    def __str__(self) :
        return ('w' if self.color == 'white' else 'b') +'Q'

''' PAWN '''
class Pawn(Piece) :
    def __init__(self, pos, color, board) :
        super().__init__(pos, color, board)
        img_path = 'img/' + color[0] + '_pawn.png'
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (board.tile_width - 35, board.tile_height - 35))
        self.notation = ' '
        self.value = 1
        
    def get_possible_moves(self, board):
        output = []
        new_y = []
        if self.color == 'white' :
            new_y.append(self.y+1)
            if not self.has_moved :
                new_y.append(self.y+2)
        elif self.color == 'black' :
            new_y.append(self.y-1)
            if not self.has_moved :
                new_y.append(self.y-2)

        for y in new_y :
            new_pos = (self.x,y)
            if new_pos[1] < 8 and new_pos[1] >= 0 :
                output.append(board.get_square_from_pos(new_pos))
            
        return output

    def get_moves(self, board):
        output = []
        for square in self.get_possible_moves(board):
            if square.occupying_piece != None:
                break
            else:
                output.append(square)

        if self.color == 'white' :
            new_y = self.y+1
        elif self.color == 'black' :
            new_y = self.y-1

        if new_y < 8 and new_y >= 0 :
            if self.x+1 < 8 :
                new_pos_right = board.get_square_from_pos((self.x+1,new_y))
                if (new_pos_right.occupying_piece is not None
                    and self.x+1 < 8 ) : 
                        if new_pos_right.occupying_piece.color != self.color :
                            output.append(new_pos_right)
            if self.x-1 >= 0 :
                new_pos_left = board.get_square_from_pos((self.x-1,new_y))
                if (new_pos_left.occupying_piece is not None
                    and self.x-1 >= 0 ):
                        if new_pos_left.occupying_piece.color != self.color :
                            output.append(new_pos_left)
        return output
    
    def attacking_squares(self, board):
        moves = self.get_moves(board)
        return [i for i in moves if i.x != self.x]

    def __str__(self) :
        return ('w' if self.color == 'white' else 'b') +'P'

''' BISHOP '''
class Bishop(Piece) :
    def __init__(self, pos, color, board) :
        super().__init__(pos, color, board)
        img_path = 'img/' + color[0] + '_bishop.png'
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (board.tile_width - 20, board.tile_height - 20))
        self.notation = 'B'
        self.value = 3
        
    def get_possible_moves(self,board) :
        output = []
        
        moves_ne = []
        for i in range(1,8) :
            if self.x+i > 7 or self.y-i < 0 :
                break
            moves_ne.append(board.get_square_from_pos(
                (self.x+i,self.y-i)
            ))
        output.append(moves_ne)
        
        moves_nw = []
        for i in range(1,8) :
            if self.x-i < 0 or self.y-i < 0 :
                break
            moves_nw.append(board.get_square_from_pos(
                (self.x-i,self.y-i)
            ))
        output.append(moves_nw)
        
        moves_sw = []
        for i in range(1,8) :
            if self.x-i < 0 or self.y+i > 7 :
                break
            moves_sw.append(board.get_square_from_pos(
                (self.x-i,self.y+i)
            ))
        output.append(moves_sw)
        
        moves_se = []
        for i in range(1,8) :
            if self.x+i > 7 or self.y+i > 7 :
                break
            moves_se.append(board.get_square_from_pos(
                (self.x+i,self.y+i)
            ))
        output.append(moves_se)

        return output
    
    def __str__(self) :
        return ('w' if self.color == 'white' else 'b') +"B"

''' ROOK '''
class Rook(Piece) :
    def __init__(self, pos, color, board) :
        super().__init__(pos, color, board)
        img_path = 'img/' + color[0] + '_rook.png'
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (board.tile_width - 20, board.tile_height - 20))
        self.notation = 'R'
        self.value = 5
        
    def get_possible_moves(self, board):
        output = []
        
        moves_east = []
        for x in range(self.x +1, 8) :
            moves_east.append(board.get_square_from_pos(
                (x,self.y)
            ))
        output.append(moves_east)
        
        moves_west = []
        for x in range(self.x)[::-1] :
            moves_west.append(board.get_square_from_pos(
                (x,self.y)
            ))
        output.append(moves_west)
        
        moves_north = []
        for y in range(self.y)[::-1] :
            moves_north.append(board.get_square_from_pos(
                (self.x,y)
            ))
        output.append(moves_north)
        
        moves_south = []
        for y in range(self.y+1, 8) :
            moves_south.append(board.get_square_from_pos(
                (self.x,y)
            ))
        output.append(moves_south)
        
        return output

    def __str__(self) :
        return ('w' if self.color == 'white' else 'b') +'R'

''' KNIGHT '''
class Knight(Piece) :
    def __init__(self, pos, color, board) :
        super().__init__(pos, color, board)
        img_path = 'img/' + color[0] + '_knight.png'
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (board.tile_width - 20, board.tile_height - 20))
        self.notation = 'N'
        self.value = 3
        
    def get_possible_moves(self, board):
        output = []
        moves = [(1,2),
                 (1,-2),
                 (-1,2),
                 (-1,-2),
                 (2,1),
                 (2,-1),
                 (-2,1),
                 (-2,-1)]
        for move in moves :
            if (self.x + move[0] < 8
            and self.x + move[0] >= 0
            and self.y + move[1] < 8
            and self.y + move[1] >= 0) :
                output.append([
                    board.get_square_from_pos(
                        (self.x + move[0], self.y + move[1])
                        )
                    ])
        return output

    def __str__(self) :
        return ('w' if self.color == 'white' else 'b') +'N'
