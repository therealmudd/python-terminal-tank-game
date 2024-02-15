from canvas import Canvas
import keyboard
import random
import time
from useful_functions import *

canvas = Canvas(50, 30)
my_tank = None
bullets = []
tanks = []
obstacles = []
pickups = []

class Pickup:
    def __init__(self, x = None, y = None, type = None):
        self.x = x or random.randrange(0, canvas.width-1)
        self.y = y or random.randrange(0, canvas.height-1)
        self.type = type or random.choice(["S", "B"])
        self.tick = 0

    def collect(self):
        for tank in tanks:
            if self.x in range(tank.x-1, tank.x+1+1)\
            and self.y in range(tank.y-1, tank.y+1+1):
                return tank
    
    def show(self):
        #canvas.draw_square(self.x-1, self.y-1, 2, ":")
        stroke = canvas.coloured((10, 200, 100), "*") if self.type == "S" else canvas.coloured((200, 10, 100), "*") 
        if self.tick < 4:
            canvas.set(self.x, self.y-1, stroke); canvas.set(self.x-1, self.y, stroke)
            canvas.set(self.x, self.y+1, stroke); canvas.set(self.x+1, self.y, stroke)
        else:
            canvas.set(self.x-1, self.y-1, stroke); canvas.set(self.x-1, self.y+1, stroke)
            canvas.set(self.x+1, self.y+1, stroke); canvas.set(self.x+1, self.y-1, stroke)
        canvas.set(self.x, self.y, self.type)
        self.tick = (self.tick + 1) % 8
        

class Obstacle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
    
    def show(self):
        r, g, b = 112, 45, 3
        canvas.draw_square(self.x, self.y, self.size, canvas.coloured((166, 120, 93),"^"))


class Bullet:
    def __init__(self, x, y, direction, colour):
        self.x = x
        self.y = y
        self.dir = direction
        self.colour = colour
    
    def move(self):
        self.x += self.dir[0]
        self.y += self.dir[1]
    
    def hit(self):
        for bullet in bullets:
            if bullet != self:
                if self.x == bullet.x and self.y == bullet.y:
                    return bullet

        for tank in tanks:
            if self.x in range(tank.x-1, tank.x+1+1)\
            and self.y in range(tank.y-1, tank.y+1+1):
                return tank
        
        for obstacle in obstacles:
            if self.x in range(obstacle.x, obstacle.x+obstacle.size+1)\
            and self.y in range(obstacle.y, obstacle.y+obstacle.size+1):
                return obstacle

        return False 

    def show(self):
        r, g, b = self.colour
        canvas.set(self.x, self.y, canvas.coloured((r,g,b),"*"))


class Tank:
    def __init__(self, x, y, colour=[255, 255, 255], controls="wasdk", id=0):
        self.x = x
        self.y = y
        self.dir = [1, 0]
        self.speed = 1
        self.hp = 3
        self.boost = {"S": 0, "B": 0}
        self.controls = controls
        self.colour = colour
        self.id = id
        

    def move(self, dp = None):
        if dp:
            dx, dy = dp
        else:
            UP, LEFT, DOWN, RIGHT = self.controls[:4]
            dx = keyboard.is_pressed(RIGHT) - keyboard.is_pressed(LEFT)
            dy = keyboard.is_pressed(DOWN) - keyboard.is_pressed(UP)

        self.speed = 2 if self.boost["S"] else 1 

        self.x += dx*self.speed
        self.y += dy*self.speed
        for obstacle in obstacles:
            if self.x in range(obstacle.x, obstacle.x+obstacle.size+1)\
            and self.y in range(obstacle.y, obstacle.y+obstacle.size+1):
                self.x -= dx*self.speed
                self.y -= dy*self.speed

        if self.x not in range(1, canvas.width-1) or self.y not in range(1, canvas.height-1):
            self.x -= dx*self.speed
            self.y -= dy*self.speed

        if dx or dy:
            self.dir = [dx, dy]
        
        # Deplete boost
        self.boost["S"] = max(self.boost["S"] - 1, 0)
        self.boost["B"] = max(self.boost["B"] - 1, 0)
    
    def shoot(self, is_shoot = None):
        if not is_shoot: 
            SHOOT = self.controls[-1]
            is_shoot = keyboard.is_pressed(SHOOT)
        if is_shoot:
            bullets.append(
                Bullet(self.x+ self.dir[0]*2, self.y + self.dir[1]*2, self.dir, self.colour)
                )
            if self.boost["B"]:
                bullets.extend([
                    Bullet(self.x+ 1 + self.dir[0]*2, self.y + self.dir[1]*2, self.dir, self.colour),
                    Bullet(self.x- 1 + self.dir[0]*2, self.y + self.dir[1]*2, self.dir, self.colour),
                    Bullet(self.x+ self.dir[0]*2, self.y + 1 + self.dir[1]*2, self.dir, self.colour),
                    Bullet(self.x+ self.dir[0]*2, self.y - 1 + self.dir[1]*2, self.dir, self.colour)
                ])

    def show(self):
        r, g, b = self.colour
        stroke = canvas.coloured((r, g, b), "#")
        canvas.draw_square(self.x-1, self.y-1, 2, stroke)
        canvas.set(self.x+ self.dir[0]*2, self.y + self.dir[1]*2, stroke)
        canvas.set(self.x, self.y, str(self.hp))


# AI for tank
'''
Idea:
> make tank stay (x + k) distance away from player 
    where k is an addtional distance if an obstacle is in the way

> since tank can only shoot at certain angles, tank can only
    move to a place where the bullet can reach player

> shoot when tank is in a good distance and angle

> dodge incoming bullets by going in the direction perpendicular
    to the velocity of the bullet

> Damn, that's a lot to implement
'''

class AI(Tank):
    def __init__(self, x, y, colour=[255, 255, 255], controls="wasdk", id=0):
        super().__init__(x, y, colour, controls, id)
        self.going = False

    def stay_away_from_player(self, other : Tank):
        d = dis(self.x, self.y, other.x, other.y)
        dx, dy = 0, 0
        if d < 20: 
            angle = ang(other.x, other.y, self.x, self.y)
            dx = round(lendir_x(1, angle))
            dy = round(lendir_y(1, angle))
        if d > 25:
            angle = ang(self.x, self.y, other.x, other.y)
            dx = round(lendir_x(1, angle))
            dy = round(lendir_y(1, angle))
        
        return [dx, dy]

    def detect_incoming_bullet(self):
        # Finding the closest incoming bullet
        closest, min_dist = None, 100000
        for bullet in bullets:
            if bullet.colour == self.colour: continue
            d = dis(bullet.x, bullet.y, self.x, self.y)
            if d < min_dist:
                closest, min_dist = bullet, min_dist
        if not closest: return

        # Check if that bullet is gonna hit the tank
        bullet = closest
        for dp in range(1000):
            dx = bullet.x + bullet.dir[0] * dp
            dy = bullet.y + bullet.dir[1] * dp
            dx, dy = round(dx), round(dy)
            if dx in range(self.x-1, self.x+1+1)\
            and dy in range(self.y-1, self.y+1+1):
                return bullet
    
    def react_to_incoming_bullet(self, bullet):
        angle = ang(0, 0, bullet.dir[0], bullet.dir[1])

        # THIS FLOPPED
        # xflip = 2*(self.x < canvas.width/2)-1
        # yflip = 2*(self.y < canvas.height/2)-1
        # if self.x == canvas.width//2: xflip = random.choice([1, -1])
        # if self.y == canvas.height//2: yflip = random.choice([1, -1])

        xflip, yflip = 1, 1

        dx = round(lendir_x(1, angle + math.pi/2 * xflip))
        dy = round(lendir_y(1, angle + math.pi/2 * yflip))
        return [dx, dy]


    def shoot_at_player(self, other):
        d = dis(self.x, self.y, other.x, other.y)
        if 20 < d < 25:
            angle = ang(self.x, self.y, other.x, other.y)
            dx = round(lendir_x(1, angle))
            dy = round(lendir_y(1, angle))
            if self.dir[0] != dx or self.dir[1] != dy:
                return [dx, dy], True
            return [0, 0], True
        return [0, 0], False
# ----------------------------------------------------------------
#                             Start                              #
# ----------------------------------------------------------------

tanks = [
    Tank(1*canvas.width//4, 1*canvas.height//4, colour = [89, 208, 217], controls="wasdr", id=1),
    Tank(3*canvas.width//4, 3*canvas.height//4, colour = [181, 29, 171], controls="ijklp", id=2)
    ]

obstacles = [
    Obstacle(random.randint(0, canvas.width), 
             random.randint(0, canvas.height), 
             random.randint(2, 5))
    for _ in range(6)
]

pickups = [
    Pickup(canvas.width//2, canvas.height//2, "S"),
    Pickup(canvas.width//2, canvas.height//2+10, "B")
]

pickup_times = [0, 0] # Use [1, 1] to activate pickups    


while True:
    canvas.clear()

    for i in range(len(pickup_times)):
        pickup_times[i] += sign(pickup_times[i])
        if pickup_times[i] == 80:
            pickup_times[i] = 0
            pickups.append(Pickup())


    for obstacle in obstacles:
        obstacle.show()

    for pickup in pickups:
        tank = pickup.collect()
        if tank:
            pickup_times[pickups.index(pickup)] = 1
            pickup_type = pickup.type
            pickups.remove(pickup); del pickup
            tank.boost[pickup_type] = 30
            continue
        pickup.show()

    for bullet in bullets:
        bullet.move()
        if bullet.x not in range(0, canvas.width)\
        or bullet.y not in range(0, canvas.height):
            bullets.remove(bullet); del bullet
            continue
        
        deleted = False
        collision = bullet.hit()
        if collision: bullets.remove(bullet); del bullet; deleted = True
        if isinstance(collision, Bullet):
            bullets.remove(collision)
            del collision
        elif isinstance(collision, Tank):
            collision.hp -= 1
            if collision.hp < 0: tanks.remove(collision); del collision
        elif isinstance(collision, Obstacle):
            pass
        if deleted: continue
        bullet.show()
    
    for tank in tanks:
        dp = None
        is_shoot = False
        if type(tank) == AI:
            other = tanks[0] if tank == tanks[1] else tanks[1]
            dp, is_shoot = tank.shoot_at_player(other)

            b = tank.detect_incoming_bullet()
            if b:
                dp = tank.react_to_incoming_bullet(b)
            elif not b and not is_shoot:
                dp = tank.stay_away_from_player(other)
        tank.move(dp)
        tank.shoot(is_shoot)
        tank.show()

    canvas.show(0.1)

    if len(tanks) == 1:
        print("GAME OVER!")
        time.sleep(1)
        break
