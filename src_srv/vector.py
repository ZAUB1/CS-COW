import math;

class Vector2:
    def __new__(self, x, y):
        self.x = x;
        self.y = y;

        self.length = math.sqrt(pow(self.x, 2) + pow(self.y, 2));

        return [self.x, self.y];