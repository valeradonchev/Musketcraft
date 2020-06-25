import numpy as np


class SpawnEvent():
    # when units are detected, units are spawned
    def __init__(self, x, y, target, count, radius, spawn):
        self.coords = np.array([x, y])
        self.target = target
        self.count = count
        self.spawn = spawn
        self.radius = radius

    def dist(self, coords):
        # measure straight line distance Company to coords
        return np.linalg.norm(self.coords - coords)

    def check(self, units):
        detect = [un for un in units if un.team == self.target]
        number = sum([1 for u in detect if self.dist(u.coords) < self.radius])
        if number >= self.count:
            for unit in self.spawn:
                unit.AIcommand(self.coords, True)
            return units + self.spawn
        return units
