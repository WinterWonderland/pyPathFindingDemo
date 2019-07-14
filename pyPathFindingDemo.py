from game import Board

board = Board(width = 2048, 
              height = 1024, 
              percentage_of_wall_fields = 0.2, 
              fps=30)
board.run()
