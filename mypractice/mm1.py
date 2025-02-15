import random

def simulate_mm1(arrival_rate, service_rate, max_time):
    clock = 0
    queue_length = 0
    num_customers_served = 0
    total_wait_time = 0
    server_busy_time = 0
    next_arrival = random.expovariate(arrival_rate)
    print("next arival values are1000011110101 : ", next_arrival)
    next_departure = float('inf')  # No departure scheduled yet
    print("next departure values are1000011110101: ", next_departure)
    event_log = []
    print("Event log values are1000011110101", event_log)

    while clock < max_time:
        print("max time is12300001230000 : ", max_time)
        if next_arrival < next_departure:  # Arrival event
            clock = next_arrival
            print("clock values are :+++ ", clock)
            print("next arrival values are :00000 ", next_arrival)
            queue_length += 1
            print("queue length values are :11111 ",queue_length)
            event_log.append((clock, "Arrival"))
            next_arrival = clock + random.expovariate(arrival_rate)
            print("next arrival values are :22222 ",next_arrival)
            if queue_length == 1:  # Server was idle
                service_time = random.expovariate(service_rate)
                print("service time values are :33333 ",service_time)
                next_departure = clock + service_time
                print("next departure values are : 44444 ",next_departure)
                server_busy_time += service_time
                print("server busy time values are : 5555",server_busy_time)
        else:  # Departure event
            clock = next_departure
            print("clock values are :6666 ",clock)
            queue_length -= 1
            print("queue length values are 66666: ",queue_length)
            num_customers_served += 1
            print("num customers served values are66666 : ",num_customers_served)
            event_log.append((clock, "Departure"))
              
            if queue_length > 0:
                service_time = random.expovariate(service_rate)
                print("service time values are : 7777",service_time)
                next_departure = clock + service_time
                print("next departure values are 7777: ",next_departure)
                server_busy_time += service_time
                print("server busy time values are :7777 ",server_busy_time)
            else:
                next_departure = float('inf')  # Server idle
                print("next departure values are : 88888",next_departure)

    utilization = server_busy_time / max_time
    return {
        "Num Customers Served": num_customers_served,
        "Server Utilization": utilization,
        "Event Log": event_log,
    }

# Example usage
results = simulate_mm1(arrival_rate=5, service_rate=7, max_time=100)
print("Num Customers Served:", results["Num Customers Served"])
print("Server Utilization:", results["Server Utilization"])
