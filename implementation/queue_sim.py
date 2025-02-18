#!/usr/bin/env python3

import argparse
import csv
import collections
import logging
import matplotlib.pyplot as plt
import numpy as np
from random import expovariate, randrange, sample, seed

from libs.discrete_event_sim import Simulation, Event
# One possible modification is to use a different distribution for job sizes or and/or interarrival times.
# Weibull distributions (https://en.wikipedia.org/wiki/Weibull_distribution) are a generalization of the
# exponential distribution, and can be used to see what happens when values are more uniform (shape > 1,
# approaching a "bell curve") or less (shape < 1, "heavy tailed" case when most of the work is concentrated
# on few jobs).

# To use Weibull variates, for a given set of parameter do something like
from libs.workloads import weibull_generator
# gen = weibull_generator(shape, mean)
#
# and then call gen() every time you need a random variable


# columns saved in the CSV file
CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w','queue_size', 'quantum', 'weibull_shape']
#CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w', 'queue_size', 'waiting_time', 'server_utilization']


class MonitorQueueSizes(Event):
    """Monitor the queue sizes, waiting times, and server utilization at regular intervals."""

    def __init__(self, interval=1):
        self.interval = interval

    def process(self, sim: 'Queues'):
        queue_lengths = [sim.queue_len(i) for i in range(sim.n)]
        #waiting_times = [sim.calculate_waiting_time(i) for i in range(sim.n)]
        #server_utilization = [sim.calculate_server_utilization(i) for i in range(sim.n)]
        
        sim.queue_size_log.append(queue_lengths)
        #sim.waiting_time_log.append(waiting_times)
        #sim.server_utilization_log.append(server_utilization)
        
        sim.schedule(self.interval, self)

class Queues(Simulation):
    """Simulation of a system with n servers and n queues.

    The system has n servers with one queue each. Jobs arrive at rate lambd and are served at rate mu.
    When a job arrives, according to the supermarket model, it chooses d queues at random and joins
    the shortest one.
    """

    def __init__(self, lambd, mu, n, d,use_rr=False, quantum=1, monitor_interval=1, shape=None):
        super().__init__()
        self.running = [None] * n  # if not None, the id of the running job (per queue)
        #self.running = [(None, None)] * n  # (job_id, remaining_time) for Round Robin
        self.queues = [collections.deque() for _ in range(n)]  # FIFO queues of the system
        # NOTE: we don't keep the running jobs in self.queues
        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
        self.lambd = lambd
        self.n = n
        self.d = d
        self.mu = mu
        self.arrival_rate = lambd * n  # frequency of new jobs is proportional to the number of queues
        self.queue_size_log = []  # Initialize queue_size_log
        #self.waiting_time_log = []  # Initialize waiting time log
        #self.server_utilization_log = []  # Initialize server utilization log
        self.waiting_times =[]  # Initialize the list to store waiting times for RR

        self.shape = shape  # Ensure shape is initialized
        self.use_rr = use_rr
        self.quantum = quantum
        self.schedule(self.generate_interarrival_time(), Arrival(0)) # schedule the first arrival
        self.schedule(0, MonitorQueueSizes(monitor_interval))
    
    def calculate_waiting_time(self, queue_index):
        queue = self.queues[queue_index]
        if queue:
            total_waiting_time = sum(self.t - self.arrivals[job_id] for job_id in queue)
            return total_waiting_time / len(queue)
        return 0

    def calculate_server_utilization(self, server_index):
        if self.running[server_index] is not None:
            return 1  # Server is busy
        return 0  # Server is idle
    
    def generate_interarrival_time(self):
        if self.shape:
            return weibull_generator(self.shape, 1 / self.lambd)()
        else:
            return expovariate(self.arrival_rate)

    def generate_service_time(self):
        if self.shape:
            return weibull_generator(self.shape, 1 / self.mu)()
        else:
            return expovariate(self.mu)    
    
    def schedule_arrival(self, job_id):
        """Schedule the arrival of a new job."""

        # schedule the arrival following an exponential distribution, to compensate the number of queues the arrival
        # time should depend also on "n"

        # memoryless behavior results in exponentially distributed times between arrivals (we use `expovariate`)
        # the rate of arrivals is proportional to the number of queues
        #logging.debug(f"Scheduling arrival of job {job_id}")
        self.schedule(self.generate_interarrival_time(), Arrival(job_id))
    
    def schedule_completion(self, job_id, queue_index, remaining_time=None):
        if self.use_rr:
            if remaining_time is None: #it generates a new service time.
                remaining_time = self.generate_service_time()
            if isinstance(remaining_time, tuple):#for exception cases only,is a tuple, it extracts the second element (the remaining time)
                remaining_time = remaining_time[1]
                
            if remaining_time > self.quantum: #it schedules an interruption after the quantum time:
                self.schedule(self.quantum, Completion(job_id, queue_index, remaining_time - self.quantum, True))
            else: #is less than or equal to the quantum, it schedules the job completion directly:
                self.schedule(remaining_time, Completion(job_id, queue_index, 0, False))
        else:
            self.schedule(self.generate_service_time(), Completion(job_id, queue_index, 0, False))
  
    def supermarket_decision(self):
        sample_queues = sample(range(self.n), self.d)
        return min(sample_queues, key=self.queue_len)
    
    def queue_len(self, i):
        """Return the length of the i-th queue.
        
        Notice that the currently running job is counted even if it is not in self.queues[i]."""

        return (self.running[i] is not None) + len(self.queues[i])


class Arrival(Event):
    def __init__(self, job_id):
        self.id = job_id

    def process(self, sim: Queues):
        sim.arrivals[self.id] = sim.t
        if sim.d > 1:
            queue_index = sim.supermarket_decision()
        else:
            queue_index = randrange(sim.n)

        if sim.running[queue_index] is None:
            sim.running[queue_index] = (self.id, sim.generate_service_time())
            sim.schedule_completion(self.id, queue_index, sim.running[queue_index])
        else:
            sim.queues[queue_index].append(self.id)
            
        sim.schedule_arrival(self.id + 1)
class Completion(Event):
    """Job completion."""

    def __init__(self, job_id, queue_index, remaining_time, is_interruption):
        self.job_id = job_id  # The ID of the job that is completing
        self.queue_index = queue_index  # The index of the queue where the job was running
        self.remaining_time = remaining_time  # Remaining execution time for Round Robin (0 for FIFO)
        self.is_interruption = is_interruption  # Flag indicating if this is a Round Robin interruption
        
        
    def process(self, sim: Queues):
        queue_index = self.queue_index
        current_job_id, _ = sim.running[queue_index]  # Get the currently running job ID

        # If this is not a Round Robin interruption, it's a true completion
        if not self.is_interruption:
            #logging.info(f"current_job_id: {current_job_id}, self.job_id: {self.job_id}")
            assert current_job_id == self.job_id  # Verify that the completing job is the one running
            sim.completions[self.job_id] = sim.t  # Record the completion time
            
            # Calculate the waiting time for Round Robin, considering interruptions
            arrival_time = sim.arrivals[self.job_id]
            completion_time = sim.t
            waiting_time = completion_time - arrival_time  # Total time in the system

            # Add the waiting time to a list to store waiting times for all jobs
            sim.waiting_times.append(waiting_time)  # You'll need to initialize this list in the Queues class

        queue = sim.queues[queue_index]  # Get the queue
        if queue:  # If the queue is not empty
            if self.is_interruption:  # If this is a Round Robin interruption
                sim.queues[queue_index].append(current_job_id)  # Put the interrupted job back in the queue
            new_job_id = queue.popleft()  # Get the next job from the queue
            sim.running[queue_index] = (new_job_id, sim.generate_service_time())  # Assign the new job to the server
            # Schedule the completion of the new job, passing remaining time if it's Round Robin
            sim.schedule_completion(new_job_id, queue_index, sim.running[queue_index]) 
        else:  # If the queue is empty
            if self.is_interruption:  # If this is a Round Robin interruption
                # Reschedule the interrupted job with its remaining time
                sim.running[queue_index] = (current_job_id, self.remaining_time)  
                sim.schedule_completion(current_job_id, queue_index, self.remaining_time)
            else:  # If it's a true completion and the queue is empty
                sim.running[queue_index] = (None, None)  # No job is running on this queue    