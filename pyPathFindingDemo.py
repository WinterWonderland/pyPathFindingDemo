from game import Board, SearchOptimization

board = Board(width=1024, 
              height=768, 
              percentage_of_wall_fields=1 / 3, 
              fps=30,
              optimization=SearchOptimization.a_star)
board.run()
