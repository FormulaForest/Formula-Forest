import os
print("Current working directory:", os.getcwd())
print("Absolute path to Propulsion theory:", os.path.abspath("../Propulsion theory"))
print("Does F_prop1.csv exist?", os.path.exists("../Propulsion theory/F_prop1.csv"))

