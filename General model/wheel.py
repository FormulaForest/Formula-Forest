class Wheel:
    def __init__(self, radius, width, mass, material):
        self.radius = radius  # in meters
        self.width = width  # in meters
        self.mass = mass  # in kilograms
        self.material = material  # string describing the material

    def moment_of_inertia(self):
        # Assuming the wheel is a solid cylinder
        return 0.5 * self.mass * self.radius ** 2
                                        # not always going to be a fair assumption

    def force_due_to_gravity(self, gravity=9.81):
        # Force due to gravity (weight)
        return self.mass * gravity

    def contact_patch_area(self):
        # Simplified contact patch area calculation
        return self.width * (self.radius / 100)  # assuming 1/100th of the radius is in contact
        # we will likely be dealing with a incredibly small contact patch -- we adjusted to 1/100th of the radius
        # This is a simplification and should be adjusted based on actual tire characteristics

    def __str__(self):
        return (f"Wheel(radius={self.radius}, width={self.width}, mass={self.mass}, "
                f"material='{self.material}')")


# Example usage
if __name__ == "__main__":
    f1_wheel = Wheel(radius=0.33, width=0.305, mass=10, material="Carbon Fiber")
    print(f1_wheel)
    print(f"Moment of Inertia: {f1_wheel.moment_of_inertia()} kg*m^2")
    print(f"Force due to Gravity: {f1_wheel.force_due_to_gravity()} N")
    print(f"Contact Patch Area: {f1_wheel.contact_patch_area()} m^2")

class Bearing:
        def __init__(self, friction_coefficient):
            self.friction_coefficient = friction_coefficient

        def friction_force(self, normal_force):
            # Friction force = friction coefficient * normal force
            return self.friction_coefficient * normal_force
        









import numpy as np
import matplotlib.pyplot as plt

class Wheel:
    def __init__(self, radius, mass, material, is_hollow=False):
        self.radius = radius  # meters
        self.mass = mass  # kg
        self.material = material  # Material properties (dict)
        self.is_hollow = is_hollow
        self.position = np.array([0.0, radius])  # (x, y) position
        self.velocity = np.array([2.0, 0.0])  # Initial velocity (m/s)
        self.angular_velocity = 0.0  # rad/s
        self.g = 9.81  # Gravity (m/s^2)
        self.dt = 0.01  # Time step (s)
        self.force = np.array([0.0, -self.mass * self.g])
        
        # Moment of inertia
        if is_hollow:
            self.inertia = 0.5 * mass * radius ** 2  # Hollow cylinder
        else:
            self.inertia = 0.5 * mass * radius ** 2  # Solid cylinder
        
        # Friction properties
        self.mu = material['friction']  # Coefficient of rolling friction
        self.restitution = material['restitution']  # Elasticity of bounce
        
        # Structural stability (stress calculations)
        self.yield_strength = material['yield_strength']  # Maximum stress before deformation
        
    def get_normal_force(self):
        if self.position[1] <= self.radius:  # Contact with ground
            return self.mass * self.g
        return 0.0
    
    def get_friction_force(self, normal_force):
        return -self.mu * normal_force  # Opposing motion
    
    def get_air_resistance(self):
        drag_coefficient = 0.47  # Approx. for a cylinder
        air_density = 1.225  # kg/m³
        area = np.pi * self.radius ** 2
        return -0.5 * drag_coefficient * air_density * area * self.velocity[0]**2 * np.sign(self.velocity[0])
    
    def update(self):
        normal_force = self.get_normal_force()
        friction_force = self.get_friction_force(normal_force)
        air_resistance = self.get_air_resistance()
        
        net_force_x = friction_force + air_resistance
        acceleration_x = net_force_x / self.mass
        self.velocity[0] += acceleration_x * self.dt
        self.position[0] += self.velocity[0] * self.dt
        
        if self.position[1] <= self.radius:  # Bouncing effect
            self.velocity[1] = -self.velocity[1] * self.restitution
        else:
            self.velocity[1] -= self.g * self.dt
        self.position[1] += self.velocity[1] * self.dt
        
        # Rotational motion
        torque = friction_force * self.radius
        angular_acceleration = torque / self.inertia
        self.angular_velocity += angular_acceleration * self.dt
        
    def check_stability(self):
        stress = (self.mass * self.g) / (np.pi * self.radius ** 2)  # Approx. stress calculation
        return stress < self.yield_strength
    
    def simulate(self, time):
        times = np.arange(0, time, self.dt)
        positions = []
        
        for t in times:
            self.update()
            positions.append(self.position.copy())
        
        return np.array(positions)

# Define material properties
rubber = {'friction': 0.03, 'restitution': 0.8, 'yield_strength': 10e6}  # Example material properties

# Create and simulate the wheel
wheel = Wheel(radius=0.05, mass=0.2, material=rubber, is_hollow=False)
positions = wheel.simulate(2)

# Plot motion
plt.plot(positions[:, 0], positions[:, 1])
plt.xlabel("Horizontal Position (m)")
plt.ylabel("Vertical Position (m)")
plt.title("Wheel Rolling and Bouncing Simulation")
plt.show()