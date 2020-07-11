import numpy as np


class SpawnEvent():
    # when units are detected, units are spawned
    def __init__(self, x, y, target, count, radius, spawn):
        self.coords = np.array([x, y])
        self.target = target
        self.count = count
        self.spawn = spawn
        self.radius = radius
        self.triggered = False

    def distanceMany(self, coords):
        if len(coords) == 0:
            return []
        return np.linalg.norm(self.coords[None, :] - np.array(coords), axis=1)

    def check(self, units):
        detect = [un for un in units if un.team == self.target]
        detDist = self.distanceMany([un.coords for un in detect])
        number = sum([1 for d in detDist if d < self.radius])
        if number >= self.count:
            for unit in self.spawn:
                unit.AIcommand(self.coords, True)
                self.triggered = True
            return units + self.spawn
        return units
