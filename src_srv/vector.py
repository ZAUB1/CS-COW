import math;

class Vector2:
    def __init__(self, x, y):
        self.x = x;
        self.y = y;

        self.length = math.sqrt(pow(self.x, 2) + pow(self.y, 2));

    def coords(self):
        return [self.x, self.y];

    def Set(self, x, y):
        self.x = x;
        self.y = y;