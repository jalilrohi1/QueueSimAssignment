from libs.discrete_event_sim import Simulation, Event
import logging

class TurnOn(Event):
    def process(self, sim):
        sim.log_info("Light turned ON")
        sim.schedule(5, TurnOff())  # Turn off after 5 time units

class TurnOff(Event):
    def process(self, sim):
        sim.log_info("Light turned OFF")
        sim.schedule(5, TurnOn())  # Turn on again after 5 time units

class LightSimulation(Simulation):
    def __init__(self):
        super().__init__()
        self.schedule(1, TurnOn())  # Turn on after 1 time unit


sim = LightSimulation()
# Configure logging to output to the console
logging.basicConfig(level=logging.INFO, format='%(message)s')

sim.run(90)  # Run the simulation for 10 time units