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

        sim.queue_size_log.append(queue_lengths)
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
        self.arrivals_log = {}  # dictionary mapping job id to arrival time
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
        #self.waiting_times = collections.defaultdict(list)  # Initialize waiting times dictionary
        self.shape = shape  # Ensure shape is initialized
        self.use_rr = use_rr
        self.quantum = quantum
        self.schedule(self.generate_interarrival_time(), Arrival(0)) # schedule the first arrival
        self.schedule(0, MonitorQueueSizes(monitor_interval))

        
    def generate_interarrival_time(self):
        return weibull_generator(self.shape, 1 / (self.lambd*self.n))() if self.shape else expovariate(self.lambd * self.n)

    def generate_service_time(self):
        return weibull_generator(self.shape, 1 / self.mu)() if self.shape else expovariate(self.mu)
    
    def supermarket_decision(self):
        if self.d == 1:  # Special case for d=1
            return randrange(self.n)
        else:
            sample_queues = sample(range(self.n), self.d)
            return min(sample_queues, key=lambda i: len(self.queues[i]))
        
    def schedule_arrival(self, job_id):
        self.schedule(self.generate_interarrival_time(), Arrival(job_id))

    def schedule_completion(self, job_id, queue_index, execution_time):
        if self.use_rr:
            self.schedule_completion_rr(job_id, queue_index, execution_time)
        else:
            self.schedule(execution_time, Completion(job_id, queue_index))  # Removed remaining_time and is_interruption

    def schedule_completion_rr(self, job_id, queue_index, remaining_time):
        # self.schedule(self.quantum, CompletionRR(job_id, queue_index, max(0, remaining_time - self.quantum)))     
        if remaining_time > self.quantum:
            self.schedule(self.quantum, CompletionRR(job_id, queue_index, remaining_time - self.quantum))
        else:
            self.schedule(remaining_time, CompletionRR(job_id, queue_index, 0))  # Removed is_interruption

    def queue_len(self, i):
        """Return the length of the i-th queue.
        
        Notice that the currently running job is counted even if it is not in self.queues[i]."""

        return (self.running[i] is not None) + len(self.queues[i])
class Arrival(Event):
    def __init__(self, job_id):
        self.id = job_id

    def process(self, sim: Queues):
        sim.arrivals[self.id] = sim.t
        sim.arrivals_log[self.id] = sim.t
        queue_index = sim.supermarket_decision() if sim.d > 1 else randrange(sim.n)
        
        #print(f"[Time {sim.t:.2f}] Job {self.id} arrived at queue {queue_index}, queue length: {len(sim.queues[queue_index])}")    
        if sim.running[queue_index] is None: # If the queue is empty, start the job
            execution_time = sim.generate_service_time()
            sim.running[queue_index] = (self.id, execution_time) if sim.use_rr else self.id
            sim.schedule_completion(self.id, queue_index, execution_time)
        else:
            sim.queues[queue_index].append((self.id, sim.generate_service_time()) if sim.use_rr else self.id)
        
        sim.schedule_arrival(self.id + 1)

class Completion(Event):
    def __init__(self, job_id, queue_index):  # Removed remaining_time and is_interruption
        self.job_id = job_id
        self.queue_index = queue_index

    def process(self, sim: Queues):
        queue_index = self.queue_index

        # Record completion time for non-RR jobs
        sim.completions[self.job_id] = sim.t

        queue = sim.queues[queue_index]
        if queue:
            new_job_id = queue.popleft()  # Removed new_execution_time
            new_execution_time = sim.generate_service_time()  # Generate new service time here
            sim.running[queue_index] = new_job_id
            sim.schedule_completion(new_job_id, queue_index, new_execution_time)
        else:
            sim.running[queue_index] = None

class CompletionRR(Event):
    def __init__(self, job_id, queue_index, remaining_time):
        self.job_id = job_id
        self.queue_index = queue_index
        self.remaining_time = remaining_time

    def process(self, sim: Queues):
        queue_index = self.queue_index
        current_job = sim.running[queue_index]

        # Record completion time for truly completed jobs
        if self.remaining_time == 0:
            sim.completions[self.job_id] = sim.t

        queue = sim.queues[queue_index]
        # Add the current job back to the queue with updated remaining time
        if self.remaining_time > 0:
            sim.queues[queue_index].append((self.job_id, self.remaining_time))

        # Select the next job from the queue
        new_job = queue.popleft()
        new_job_id, new_execution_time = new_job
        sim.running[queue_index] = (new_job_id, new_execution_time)
        sim.schedule_completion(new_job_id, queue_index, new_execution_time)

        # if queue:
        #     # Add the current job back to the queue with updated remaining time
        #     if self.remaining_time > 0:
        #         sim.queues[queue_index].append((self.job_id, self.remaining_time))
 
        #     # Select the next job from the queue
        #     new_job = queue.popleft()
        #     new_job_id, new_execution_time = new_job
        #     sim.running[queue_index] = (new_job_id, new_execution_time)
        #     sim.schedule_completion(new_job_id, queue_index, new_execution_time)
        # else:
        #     sim.running[queue_index] = None
