# attempt to engage enemies in sight by advancing
# for aim() of Company
# problem: controlling when flag moves, company stops when attack moving, jittering
# for target in group:
#     if self.target is None:
#         seen = self.distance(target.coords) <= I_SIGHT
#         if seen and target.size > 0 and self.allowShoot:
#             self.target = target
#             if self.moving:
#                 self.oldAngle = self.angle
#                 self.stop()
# if self.target is not None:
#     self.lookAt(self.target.coords)
#     toTarget = self.distance(self.target.coords)
#     dead = self.target.size == 0
#     if toTarget > I_SIGHT or dead or not self.allowShoot:
#         self.target = None
#         self.stop(True)
#         [infantry.aim(self.target, self.angle, self.allowShoot) for infantry in self]
#     elif self.oldAngle != self.angle:
#         if self.formed < self.size:
#             [infantry.form(self.angle, self.oldAngle, self.coords) for infantry in self]
#         else:
#             self.oldAngle = self.angle
#             self.stop(True)
#     elif toTarget > self.range and np.array_equal(self.coords, self.flag.coords):
#         self.setSpeed(self.target.coords)
#         [infantry.setSpeed(self.speed) for infantry in self]
#         self.flag.coords += self.velocity
#     else:
#         self.stop(True)
#         [infantry.aim(self.target, self.angle, self.allowShoot) for infantry in self]

# for target in group:
#             if self.target is None:
#                 dist = self.distance(target.coords) <= self.range
#                 if dist and target.size > 0 and self.allowShoot:
#                     self.target = target
#                     if self.moving:
#                         self.oldAngle = self.angle
#                         self.stop()
#         if self.target is not None:
#             self.lookAt(self.target.coords)
#             toTarget = self.distance(self.target.coords)
#             dead = self.target.size == 0
#             if toTarget > self.range or dead or not self.allowShoot:
#                 self.target = None
#                 self.stop(True)
#             elif self.oldAngle != self.angle:
#                 if self.formed < self.size:
#                     [infantry.form(self.angle, self.oldAngle, self.coords)
#                      for infantry in self]
#                 else:
#                     self.oldAngle = self.angle
#                     self.stop(True)
#             [infantry.aim(self.target, self.angle, self.allowShoot)
#              for infantry in self]
