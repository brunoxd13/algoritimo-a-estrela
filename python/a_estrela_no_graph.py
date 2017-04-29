maze = """\
#############
#       #   #
# ##### ### #
#     #     #
# ### # #####
#     #    ##
### ###### ##
###     ## ##
# ### #### ##
# ### #### ##
#   # #     #
### # # #####
#     #     S
#############
"""

NONE, WALL, FNSH, SEEN, GOOD = " ", "#", "S", ".", "+"

def solve(maze, x, y):
   found = False
   if 0 <= x < len(maze[0]) and 0 <= y < len(maze):
       if maze[y][x] == NONE:
           maze[y][x] = SEEN
           if (solve(maze, x+1, y) or solve(maze, x-1, y) or
               solve(maze, x, y+1) or solve(maze, x, y-1)):
               maze[y][x] = GOOD
               found = True
       elif maze[y][x] == FNSH:
           found = True
   return found

if __name__ == "__main__":
   maze = [list(line) for line in maze.splitlines()]
   solve(maze, 1, 8)
   for line in maze:
       print "".join(line)