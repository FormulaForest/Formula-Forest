import numpy as np
from scipy.spatial.transform import Rotation as R

class Force:

    def __init__(self, r:tuple, F:tuple):
        # two three component vectors: 
        #   one for the #D position of the vector, 
        #   one for the magnitude and direction of the force
        self.r = np.array(r)
        self.F = np.array(F)

    def convert_coords(self, S:dict):
        """
        Rotates a vector using the current quaternion.
        """
        q = S['q']

        self.r = R.from_quat(q).as_matrix() @ self.r
        self.F = R.from_quat(q).as_matrix() @ self.F

    def get_torque(self):
        d = self.r + ((np.dot(self.r, self.F) / np.dot(self.F, self.F)) * self.F)
            # finds the lever arm by which the force is applied to create the torque

        T = np.cross(d, self.F)
            # cross products the lever arm with the force

        return T