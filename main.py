# Main: http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com

# Post to Start: http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session
# Request Body:
# {
# 	“uid”: str
# }
#
# Expected Response Body:
# {
# 	“token”: str # token encoded with uid
# }

# Post to Move: http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token=[ACCESS_TOKEN]
# Request Body:
# {
# 	“action”: str //“UP”, “DOWN”, “LEFT”, “RIGHT”
# }
#
# Expected Response Body
# {
# 	“result”: str //“WALL” if a wall is hit, “SUCCESS”, “OUT_OF_BOUNDS” if outside, or “END” if end has been reached
# }

# GET maze state: http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token=[ACCESS_TOKEN]
# Expected Response Body:
# {
# 	“maze_size”: [int, int], <- [width, height], null if status is NONE or FINISHED
# 	“current_location”: [int, int], <- [xcol, ycol], null if status is NONE or FINISHED
# 	“status”: str, <- can be “PLAYING”, “GAME_OVER”, “NONE”, “FINISHED”
# 	“levels_completed”: int <- 0 indexed, 0-L, null if status is NONE or FINISHED
# 	“total_levels”: int <- L, null if status is NONE or FINISHED
# }

#


import requests

class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set(self, dim = []):
        if dim is None:
            return False
        if len(dim) < 2:
            return False
        self.width = dim[0]
        self.height = dim[1]
        return True

# Yes, I know...
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set(self, dim = []):
        if dim is None:
            return False
        if len(dim) < 2:
            return False
        self.x = dim[0]
        self.y = dim[1]
        return True


class Maze:
    def __init__(self, x, y):
        self.lenx = x
        self.leny = y
        self.mapping = []
        for i in range(x):
            self.mapping.append([])
            for j in range(y):
                self.mapping[i].append("?")

    def reset(self, size):
        self.clear()
        x = size.width
        y = size.height
        self.lenx = x
        self.leny = y
        for i in range(x):
            self.mapping.append([])
            for j in range(y):
                self.mapping[i].append("?")

    def shouldMoveTo(self, point):
        print("({0},{1})// inBounds: {2} // isVisited: {3} // isWall: {4}".format(point.x, point.y, self.isInBounds(point),
                                                                                  self.isVisited(point), self.isWall(point)))
        return self.isInBounds(point) and not self.isVisited(point) and not self.isWall(point)

    def isInBounds(self, point):
        return 0 <= point.x < self.lenx and 0 <= point.y < self.leny

    def isVisited(self, point):
        if not self.isInBounds(point):
            return False
        return self.mapping[point.x][point.y] == "*"

    def isWall(self, point):
        if not self.isInBounds(point):
            return False
        return self.mapping[point.x][point.y] == "X"

    def set(self, point, result):
        if point.x < 0 or point.x > self.lenx - 1:
            print("x = {0}: out of bounds 0-{1}".format(point.x, self.lenx - 1))
            return
        if point.y < 0 or point.y > self.leny - 1:
            print("y = {0}: out of bounds 0-{1}".format(point.y, self.leny - 1))
            return
        if result == "WALL":
            self.mapping[point.x][point.y] = "X"
        elif result == "SUCCESS":
            self.mapping[point.x][point.y] = "*"
        elif result == "END":
            self.mapping[point.x][point.y] = "!"

    def visit(self, point):
        if self.isInBounds(point):
            self.mapping[point.x][point.y] = "*"
        else:
            print("OUT OF BOUNDS!")
            assert False

    def wall(self, point):
        if self.isInBounds(point):
            self.mapping[point.x][point.y] = "X"
        else:
            print("OUT OF BOUNDS!")
            assert False

    def goal(self, point):
        if self.isInBounds(point):
            self.mapping[point.x][point.y] = "!"
        else:
            print("OUT OF BOUNDS!")
            assert False

    def dump(self):
        for i in range(self.lenx):
            for j in range(self.leny):
                print(self.mapping[i][j], end=" ")
            print()
        print()

    def clear(self):
        self.mapping = []


class MazeWD:
    startURL = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session"
    getURL = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token={0}"
    moveURL = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game?token={0}"
    UID = "105009354"

    def __init__(self):
        self.maze = Maze(0, 0)
        self.sessionToken = ""
        self.mazeSize = Size(0, 0)
        self.currentLocation = Point(0, 0)
        self.status = "NONE"
        self.completedLevels = 0
        self.totalLevels = 0

        self.stack = []

    def start(self):
        print(MazeWD.startURL)
        req = requests.post(MazeWD.startURL, {"uid": MazeWD.UID})
        json = req.json()
        self.sessionToken = json["token"]

        # TEMPORARY
        print(json)

        if self.sessionToken == "":
            print("WARNING: Empty session token")
            return False
        return True
        # Make the post request and set sessionToken


    def move(self, action, backtrack = False):
        assert action == "LEFT" or action == "RIGHT" or action == "UP" or action == "DOWN"

        target = Point(self.currentLocation.x, self.currentLocation.y)

        if action == "LEFT":
            target.x -= 1
        elif action == "RIGHT":
            target.x += 1
        elif action == "UP":
            target.y -= 1
        elif action == "DOWN":
            target.y += 1
        else:
            assert False

        if not self.maze.shouldMoveTo(target) and not backtrack:
            return False

        print("Checking ({0}/{1})".format(target.x, target.y))

        req = requests.post(MazeWD.moveURL.format(self.sessionToken), {"action": action})
        json = req.json()
        result = json["result"]

        if result == "WALL":
            self.maze.wall(target)
            return False
        elif result == "SUCCESS":
            self.maze.visit(target)
            self.currentLocation.x = target.x
            self.currentLocation.y = target.y
            if not backtrack:
                self.stack.append(action)
            return True
        elif result == "END":
            self.maze.goal(target)
            self.refreshInfo() #REFRESHES WHEN ENDING LEVEL
            return True

        # Make post request to move UP DOWN LEFT or RIGHT
    def backtrack(self):
        if len(self.stack) < 1:
            return False
        reverse = self.stack.pop()
        if reverse == "LEFT":
            self.move("RIGHT", True)
        elif reverse == "RIGHT":
            self.move("LEFT", True)
        elif reverse == "UP":
            self.move("DOWN", True)
        elif reverse == "DOWN":
            self.move("UP", True)
        else:
            print("Unexpected reverse action: {0}".format(reverse))
            assert False
        return True

    def refreshInfo(self):
        req = requests.get(MazeWD.getURL.format(self.sessionToken))
        json = req.json()

        if json["status"] == "FINISHED":
            print("SOLVING MAZE WAS A SUCCESS!")

        print(json)
        if not self.mazeSize.set(json["maze_size"]):
            print("I couldn't adjust the maze size.")
        if not self.currentLocation.set(json["current_location"]):
            print("I couldn't adjust the current location")

        self.completedLevels = json["levels_completed"]
        self.totalLevels = json["total_levels"]
        self.status = json["status"]

        self.maze.reset(self.mazeSize)
        self.stack.clear()

        self.maze.visit(self.currentLocation)

        return

    def solve(self):
        self.start()
        self.refreshInfo()
        i = 0
        while self.status == "PLAYING":
            print("Turn {0}   Maze {1}".format(i, self.completedLevels + 1))
            if self.move("LEFT"):
                print("Moved LEFT...")
            elif self.move("RIGHT"):
                print("Moved RIGHT...")
            elif self.move("UP"):
                print("Moved UP...")
            elif self.move("DOWN"):
                print("Moved DOWN...")
            elif self.backtrack():
                print("BACKTRACK...")
            else:
                print("UT OH... I'm stuck...")
                self.maze.dump()
                assert False
            print("Current Location: {0}, {1}".format(self.currentLocation.x, self.currentLocation.y))
            i += 1
            self.maze.dump()
            print()

        print(self.status)



        # Make get request and update my model of the maze
        # NOTE: do not update maze here, do that on move


# TRY A GET REQUEST!
#     req = requests.request("GET", "https://mtgjson.com/json/RIX.json")
#     json = req.json()
#     print(json["name"])
    # prints "Rivals of Ixalan"

driver = MazeWD()
driver.solve()



# Make initial Post with uid.  Store response token.
# Dump response

# Make initial Get request for maze state.
# Dump response

### While the game state is PLAYING
    # Do some movement
    # If the result is OUT_OF_BOUNDS, output error and quit.
### While the result is not END
    # Do some movement
    # If the result is OUT_OF_BOUNDS, output error and quit.














