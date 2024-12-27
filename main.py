import pygame
import pygame_menu
from pygame_menu import themes
from oue import Board
from random import randint

pygame.init()

WINDOW_SIZE = (600,600)
screen = pygame.display.set_mode(WINDOW_SIZE)

board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

class Player() :
    def get_color(self) :
        return self.color
    def is_human_player(self) :
        return self.humanPlayer
    def __str__(self) :
        string = f"Side : {self.color}\n"
        string += f"Nature : {'Human' if self.is_human_player() else 'Bot'}"
        return string

class HumanPlayer(Player) :
    def __init__(self, color) :
        self.color = color
        self.humanPlayer = True

class ComputerPlayer(Player) :
    def __init__(self, color) :
        self.color = color
        self.humanPlayer = False

    def white_points(self, board) :
        for square in board.squares :
            if square.occupying_piece is not None and square.occupying_piece.color
        
    def move(self, board) :
        for square in board.squares :
            if square.occupying_piece is not None :
                moves = square.occupying_piece.get_valid_moves(board)
                
            

def draw(display) :
    display.fill('white')
    board.draw(display)
    pygame.display.update()

rng = randint(0,1)
p1 = HumanPlayer('black' if rng == 0 else 'white')
p2 = HumanPlayer('black' if p1.color == 'white' else 'white')
def set_player_2(player_type, value) :
    global p2
    if p2.is_human_player() :
        p2 = ComputerPlayer('black' if p1.color == 'white' else 'white')
    else :
        p2 = HumanPlayer('black' if p1.color == 'white' else 'white')
    
def start() :
    running = True
    while running :
        activePlayer = p1 if board.turn == p1.color else p2
        if activePlayer.is_human_player() :
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get() :
                if event.type == pygame.QUIT :
                    board.reset_board()
                    board.setup_board()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN :
                    if event.button == 1 :
                        board.handle_click(mx, my)
            if board.is_in_checkmate('black') :
                print("White wins !")
                board.reset_board()
                board.setup_board()
                running = False
            elif board.is_in_checkmate('white'):
                print('Black wins!')
                board.reset_board()
                board.setup_board()
                running = False

        else :
            activePlayer.move(board)
            
        draw(screen)

if __name__ == '__main__' :

    mainmenu = pygame_menu.Menu('Welcome',
                                600, 400, 
                                theme=themes.THEME_SOLARIZED)
    
    mainmenu.add.button('Play', start)

    mainmenu.add.selector('Play with :', [('Human', 1), ('Computer', 2)], onchange=set_player_2)
    
    mainmenu.mainloop(screen)

