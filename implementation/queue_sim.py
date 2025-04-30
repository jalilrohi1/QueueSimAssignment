#!/usr/bin/env python3

import argparse
import csv
import collections
import heapq
import logging
import matplotlib.pyplot as plt
import numpy as np
from random import expovariate, randrange, sample, seed

from libs.discrete_event_sim import Simulation, Event


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
        #self.running = [None] * n  # if not None, the id of the running job (per queue)
        self.running = [None for _ in range(n)]  # if not None, the id of the running job
        heapq.heapify(self.events)  # treat the list as a heap
        #self.running = [(None, None) for _ in range(n)]  # (job_id, remaining_time) for Round Robin
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
            #self.schedule_completion_rr(job_id, queue_index, execution_time)
            self.schedule(min(execution_time, self.quantum),CompletionRR(job_id, queue_index, max(0, execution_time - self.quantum)))
        else:
            self.schedule(execution_time, Completion(job_id, queue_index))  # Removed remaining_time and is_interruption
        
    def queue_len(self, i):
        """Return the length of the i-th queue.
        
        Notice that the currently running job is counted even if it is not in self.queues[i]."""

        return (self.running[i] is not None) + len(self.queues[i])
class Arrival(Event):
    def __init__(self, job_id):
        self.id = job_id

    def process(self, sim: Queues):
        sim.arrivals[self.id] = sim.t       # Record arrival time for all jobs
        sim.arrivals_log[self.id] = sim.t   # Record arrival time for all jobs
        queue_index = sim.supermarket_decision() if sim.d > 1 else randrange(sim.n)
        execution_time = sim.generate_service_time()
    
        if sim.running[queue_index] is None: # If the queue is empty, start the job            
            sim.running[queue_index] = (self.id, execution_time) if sim.use_rr else self.id
            sim.schedule_completion(self.id, queue_index, execution_time)
        else:
            sim.queues[queue_index].append((self.id, execution_time) if sim.use_rr else self.id)

        sim.schedule_arrival(self.id + 1)

class Completion(Event):
    def __init__(self, job_id, queue_index):  # Removed remaining_time and is_interruption
        self.job_id = job_id
        self.queue_index = queue_index

    def process(self, sim: Queues):
        queue_index = self.queue_index
        assert sim.running[queue_index] == self.job_id
        # Record completion time for non-RR jobs

        sim.completions[self.job_id] = sim.t

        queue:collections.deque[int] = sim.queues[queue_index]
        if queue: # If the queue is not empty, start the next job
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

            # If job is fully complete, record its completion time.
        if self.remaining_time == 0:
            sim.completions[self.job_id] = sim.t
        else:
            # If the queue is empty, resume the same job immediately.
            if not sim.queues[queue_index]:
                sim.schedule_completion(self.job_id, queue_index, self.remaining_time)
                return
            else:
                # Otherwise, requeue the unfinished job.
                sim.queues[queue_index].append((self.job_id, self.remaining_time))
        
        # If there is another job waiting, pick it from the queue.
        if sim.queues[queue_index]:
            new_job = sim.queues[queue_index].popleft()
            new_job_id, new_execution_time = new_job
            sim.running[queue_index] = (new_job_id, new_execution_time)
            sim.schedule_completion(new_job_id, queue_index, new_execution_time)
        else:
            sim.running[queue_index] = None

