def setting():
    global area
    global size
    global amount
    #user chooses grid size
    size = int(input("\nSize for minesweeper grid: "))
    while size <= 0 or size > 50:
        size = int(input("\nSuitable size for minesweeper grid: "))
        
    area = [["·" for i in range(size)] for j in range(size)]

    #user chooses mine amount
    amount = int(input("Number of mines: "))
    
    global bombs
    bombs = []
    import random
    count = amount
    #count = int(size)
    while count != 0:
              
              x = random.randint(0,size-1)
              y = random.randint(0,size-1)
              inside = False
              for mine in bombs:
                  if mine.x == x and mine.y == y:
                      inside = True
                      
              if not inside:
                  bomb = Bomb(x, y)
                  bombs.append(bomb)
                  count -= 1

    return area, bombs



class Bomb():
          def __init__(self, x, y):
                    self.x = x
                    self.y = y

          def hit(self):
                    self.status = "exploded"
                    return self.status
                
          def flag(self):
                    self.status = "flagged"
                    return self.status

def output(area, size):
    for row in area:
        print(" ".join(map(str, row)))

    # super extra but put a box around
    #print("┌" + "─" * (2 * size) + "┐")
    #for row in area:
    #    print("| " + "   ".join(map(str, row)) + " |")
    #print("└" + "─" * (2 * size) + "┘")

def reveal(x, y):
          global area
          global bombs
          global size
          counter = 0
          #if (x >= 0 and x < size) and (y >= 0 and y < size):
          for mine in bombs:

                              if y < size-1 and mine.x == x and mine.y == y+1:
                                          counter += 1

                              if y > 0 and mine.x == x and mine.y == y-1:
                                          counter += 1
                                          
                              if x < size-1 and mine.x == x+1 and mine.y == y:
                                          counter += 1

                              if x > 0 and mine.x == x-1 and mine.y == y:
                                          counter += 1

                              if x < size-1 and y < size-1 and mine.x == x+1 and mine.y == y+1:
                                          counter += 1

                              if x < size-1 and y > 0 and mine.x == x+1 and mine.y == y-1:                                        
                                          counter += 1

                              if x > 0 and y < size-1 and mine.x == x-1 and mine.y == y+1:
                                          counter += 1

                              if x > 0 and y > 0 and mine.x == x-1 and mine.y == y-1:
                                          counter += 1

          area[x][y] = counter




def play():
    global size
    global amount
    area, bombs = setting()
    
    #global bombs
    count = amount
    flagged = 0
    hit = False
    while not hit:
              output(area, size)

              question = input("\nFlag or Uncover or Quit? f/u/q: ")

              if question == "f":
                        flag_x = int(input(f"Flag row coordinate (1-{size}): ")) -1
                        flag_y = int(input(f"Flag column coordinate (1-{size}): ")) -1

                        if (0 <= flag_x < size) and (0 <= flag_y < size):
                                  for mine in bombs:
                                            if mine.x == flag_x and mine.y == flag_y:
                                                      print(mine.flag())
                                                      flagged += 1
                                                      area[flag_x][flag_y] = "F"
                                                      print("Correctly flagged!")
                                                      count -= 1
                                                      print("Mines left: " , count)
                                                      
                                                      

                                  if area[flag_x][flag_y] != "F":
                                            print("No flag necessary there")
                                     


              elif question == "u":
                        x_coord = int(input(f"Row coordinate (1-{size}): ")) -1
                        y_coord = int(input(f"Column coordinate (1-{size}): ")) -1

                        if (0 <= x_coord < size) and (0 <= y_coord < size):
                                  for mine in bombs:
                                            if mine.x == x_coord and mine.y == y_coord:
                                                      print(mine.hit())
                                                      hit = True
                                                      area[x_coord][y_coord] = "M"

                                                      output(area, size)
                                                      print("You hit a mine, game over!")
                                                      
                                                      break
                                  if not hit:
                                            print("Correctly uncovered :)")
                                            #area[x_coord][y_coord] = "  "

                                            reveal(x_coord, y_coord)
                                            x = x_coord
                                            y = y_coord
                                            if area[x_coord][y_coord] == 0:
                                                if y < size-1:
                                                  reveal(x, y+1)
                                                if y > 0:
                                                  reveal(x, y-1)
                                                if x < size-1:
                                                  reveal(x+1, y)
                                                if x > 0:
                                                  reveal(x-1, y)
                                                if x > 0 and y > 0:
                                                  reveal(x-1, y-1)
                                                if x < size-1 and y < size-1:
                                                  reveal(x+1, y+1)
                                                if x < size-1 and y > 0:
                                                  reveal(x+1, y-1)
                                                if x > 0 and y < size-1:
                                                  reveal(x-1, y+1)

              elif question == "q":
                  break
              #else:
              #          continue

              if flagged == len(bombs):
                        output(area, size)
                        print(f"\nFlagged all {amount} mines correctly")
                        break

opt = input("** Do you want to play minesweeper? y/n: ")
if opt != "n":
    play()
    again = input("\n** Do you want to play minesweeper again? y/n: ")
    while again == "y":
        again = input("\n** Do you want to play minesweeper again? y/n: ")
        play()
    print("Thank you for playing :) ")

else:
    print("Ok :(")
