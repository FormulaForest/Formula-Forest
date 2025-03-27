import sympy as ap
import numpy as np
import matplotlib.pyplot as plt

class Car:

    def __init__(self, I:np.array, dt = 1e-4, m = 0.05):
        self.x = np.array([0.0, 0.0, 0.0])
        self.v = np.array([0.0, 0.0, 0.0])
        self.a = np.array([0.0, 0.0, 0.0])
        
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.omega = np.array([0.0, 0.0, 0.0])
        self.alpha = np.array([0.0, 0.0, 0.0])

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
        self.q_list = [self.q.copy()]
        self.omega_list = [self.omega.copy()]
        self.alpha_list = [self.alpha.copy()]

    def apply_forces(self, F:tuple):
        for f in F:
            self.forces.append(f)

    # def give_weight(self, ):

    def quaternion_derivative(self, q, omega):
        """
        Computes the quaternion derivative given angular velocity omega.
        """
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

        # Update linear velocity and position
        self.v += self.a * self.dt
        self.x += self.v * self.dt

        # Apply torques to update angular acceleration
        for f in self.forces:
            # print(self.I_inv)
            # print(f.F)
            # print(f.get_torque())
            # print(self.I_inv @ f.get_torque().reshape(3, 1))
            # print(self.alpha)
            self.alpha += self.I_inv @ f.T()

        # Update angular velocity
        self.omega += self.alpha * self.dt

            # Old directional vector update
        # Sigma = np.mat([[0, -self.omega[2], self.omega[1]],
        #     [self.omega[2], 0, -self.omega[0]],
        #     [-self.omega[1], self.omega[0], 0]])
        # R = np.identity(3) + Sigma * self.dt
        # self.r = R * self.r

        # Update quaternion (orientation)
        q_dot = self.quaternion_derivative(self.q, self.omega)
        self.q += q_dot * self.dt

        # Normalize quaternion to prevent drift
        self.q /= np.linalg.norm(self.q)
        
        # Store history
        self.t_list.append(self.t)
        self.x_list.append(self.x.copy())
        self.v_list.append(self.v.copy())
        self.a_list.append(self.a.copy())
        self.q_list.append(self.q.copy())
        self.omega_list.append(self.omega.copy())
        self.alpha_list.append(self.alpha.copy())

        # Reset forces
        self.forces = []
        self.a = np.array([0.0, 0.0, 0.0])
        self.alpha = np.array([0.0, 0.0, 0.0])


    def __iter__(self):
        dict = {"t": self.t, "x": self.x, "v": self.v, "a": self.a, "q": self.q, "omega": self.omega, "alpha": self.alpha}
        return iter(dict.items())


if __name__ == "__main__":
    car = Car()
    # car.apply_forces([Force(r=(0, 0, 0), F=(0, 0, 0))])
    # car.apply_forces([Force(r=(0, 0, 0), F=(0, 0, 0))])
    # car.apply_forces([Force(r=(0, 0, 0), F=(0, 0, 0))])

    # for _ in range(1000):
    #     car.update()

    # for k, v in car:
    #     print(k, v)

    # plt.plot(car.x[0], car.x[1])
    # plt.show()

    print(dict(car))