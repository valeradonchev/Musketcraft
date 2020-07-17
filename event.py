import numpy as np


class SpawnEvent():
    """ When enough units of target team are in range, spawn units

    Attributes
    ----------
    coords : float 1-D numpy.ndarray [2], >=0
        coords of center of SpawnEvent
    target : str
        team designation units must have to be detected
    count : int, >= 0
        number of unit formations to trigger event
    spawn : list of Company, Battery, Squadron
        units that will be spawned
    radius : int, >= 0
        radius within which Spawn Event checks for units
    triggered : bool
        whether this event has spawned units

    Methods
    -------
    distanceMany
        measure straight line distance SpawnEvent to list of coords
    check
        check for units, spawn units
    """

    def __init__(self, x, y, target, count, radius, spawn):
        self.coords = np.array([x, y])
        self.target = target
        self.count = count
        self.spawn = spawn
        self.radius = radius
        self.triggered = False

    def distanceMany(self, coords):
        # measure straight line distance SpawnEvent to list of coords
        if len(coords) == 0:
            return []
        return np.linalg.norm(self.coords[None, :] - np.array(coords), axis=1)

    def check(self, units):
        # check for units, spawn units
        detect = [un for un in units if un.team == self.target]
        detDist = self.distanceMany([un.coords for un in detect])
        number = sum([1 for d in detDist if d < self.radius])
        if number >= self.count:
            for unit in self.spawn:
                unit.AIcommand(self.coords, True)
                self.triggered = True
            return units + self.spawn
        return units
