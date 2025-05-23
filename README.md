# Formula-Forest
Computational models of the physics behind our racecar for the STEM Racing competitions.

## Areas of Improvement

1) Add tether line friction
2) Include the accurate position of the point of application in the definition of every force
3) Fix rotational motion aspect
4) Test and make sure the result is accurate and logical

## Wind Tunnel

In the "Wind Tunnel" folder is code and other materials for the tunnel.

### Use instructions:

1. Plug the power supply into the outlet
2. Plug the USB into your laptop
3. Run "tunnel_gui.py"
4. Calibrate the tunnel if needed
5. Using the physical dial under the tunnel, set the fan power to match the desired speed
6. When the speed stabilizes, record the data into .csv

### Calibration process:

Calibration is done by applying 1 N of force to each load cell. The load cells are numbered in this way:
1. Front vertical
2. Front horizontal
3. Back vertical
4. Back horizontal

However, if you mess up the order during the calibration, nothing will break, but you will have to stick to that new order.

### Structure of the project:

**tunnel_gui.py** - GUI of the tunnel \
**serial_reader.py** - reads the COM port and sends the data to GUI \
**calibration_matrix.txt** - saves the calibration data between sessions \
**svgplot.py** - produces the svg of the shape of the intake (needed for CAD design) \
**Arduino folder** - code that is uploaded and executed on the arduino \
**Files to print folder** - stl files of all parts that were 3d printed for the wind tunnel

### Improvements:

1. Test the tunnel
2. Design a connector between the middle section and the diffuser
3. Design the stand for the fan
4. Build the rest of the intake
5. Upgrade GUI (specific upgrades are commented in the tunnel_gui.py)

## With any questions:

Feel free to reach out to me at ltartako@caltech.edu