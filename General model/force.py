import numpy as np
from scipy.spatial.transform import Rotation as R

class Force:

    def __init__(self, F:tuple, r:tuple=None, T:tuple=None):
        # two three component vectors: 
        #   one for the #D position of the vector, 
        #   one for the magnitude and direction of the force
        self.F = np.array(F)

        if r is None:
            self.r = np.zeros(3)
            self.set_torque(T)
        else:
            self.r = np.array(r)
            self.get_torque()

    def convert_coords(self, S:dict):
        """
        Rotates a vector using the current quaternion.
        """
        coords = S['coords']

        self.r = coords.T @ self.r
        self.F = coords.T @ self.F
        self.T = coords.T @ self.T

    def get_torque(self):

        if np.array_equal(self.F, np.zeros(3)):
            self.T = np.zeros(3)
            return None

        d = self.r + ((np.dot(self.r, self.F) / np.dot(self.F, self.F)) * self.F)
            # finds the lever arm by which the force is applied to create the torque

        T = np.cross(d, self.F)
            # cross products the lever arm with the force

        self.T = T
    
    def set_torque(self, T):
        self.T = T