import sympy as ap
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

class Car:

    def __init__(self, I:np.array, dt = 1e-4, m = 0.05):
        self.x = np.array([0.0, 0.0, 0.0])
        self.v = np.array([0.0, 0.0, 0.0])
        self.a = np.array([0.0, 0.0, 0.0])
        
        self.coords = np.eye(3)
        self.omega = np.array([0.0, 0.0, 0.0])
        self.alpha = np.array([0.0, 0.0, 0.0])

        self.N = m * 9.81

        self.I = I
        self.I_inv = np.linalg.inv(I)
        
        self.t = 0 
        self.dt = dt
        self.m = m
        self.forces = []

        self.t_list = [self.t]
        self.x_list = [self.x.copy()]
        self.v_list = [self.v.copy()]
        self.a_list = [self.a.copy()]
        self.coords_list = [self.coords.copy()]
        self.omega_list = [self.omega.copy()]
        self.alpha_list = [self.alpha.copy()]
        self.N_list = [self.N]

    def apply_forces(self, F:tuple):
        for f in F:
            self.forces.append(f)

    # def give_weight(self, ):

    def rotate_coords(self):
        """
        Computes the quaternion derivative given angular velocity omega.
        """
        rotation = Rotation.from_rotvec(self.omega * self.dt)
        return rotation.apply(self.coords)


        w, x, y, z = q
        omega_x, omega_y, omega_z = omega

        # Quaternion form of angular velocity
        # omega_q = np.array([0, omega_x, omega_y, omega_z])

        # Compute q_dot = 0.5 * q * omega_q
        q_dot = 0.5 * np.array([
            -x * omega_x - y * omega_y - z * omega_z,
             w * omega_x + y * omega_z - z * omega_y,
             w * omega_y + z * omega_x - x * omega_z,
             w * omega_z + x * omega_y - y * omega_x
        ])

        return q_dot

    def update(self):

        self.t += self.dt

        # Apply forces to update linear acceleration
        for f in self.forces:
            self.a += f.F / self.m

        self.N = max(self.m * (9.81 - self.a[2]), 0)  # Normal force
        self.a[2] = max(self.a[2]-9.81, 0)  # Ensure no negative vertical acceleration

        # Update linear velocity and position
        self.v += self.a * self.dt
        self.x += self.v * self.dt

        # Apply torques to update angular acceleration
        for f in self.forces:
            self.alpha += self.I_inv @ f.T

        # Update angular velocity
        self.omega += self.alpha * self.dt

        # Update quaternion (orientation)
        self.coords = self.rotate_coords()

        # # Normalize quaternion to prevent drift
        # self.q /= np.linalg.norm(self.q)
        
        # Store history
        self.t_list.append(self.t)
        self.x_list.append(self.x.copy())
        self.v_list.append(self.v.copy())
        self.a_list.append(self.a.copy())
        self.coords_list.append(self.coords.copy())
        self.omega_list.append(self.omega.copy())
        self.alpha_list.append(self.alpha.copy())
        self.N_list.append(self.N)

        # Reset forces
        self.forces = []
        self.a = np.array([0.0, 0.0, 0.0])
        self.alpha = np.array([0.0, 0.0, 0.0])


    def __iter__(self):
        dict = {"t": self.t, "x": self.x, "v": self.v, "a": self.a, "coords": self.coords, "omega": self.omega, "alpha": self.alpha, "N": self.N}
        return iter(dict.items())


if __name__ == "__main__":
    car = Car(np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), dt=1e-4, m=0.05) #test
    print(dict(car))