import heapq
import math
import random
import statistics
import time
from datetime import datetime
from functools import partial
from multiprocessing import Manager, Pool


def generate_random(lambda_):
    return -math.log(1.0 - random.random())/lambda_


# Q1
def verify_generated_random(lambda_):
    random = [generate_random(lambda_) for i in range(1000)]

    mean = statistics.mean(random)
    variance = statistics.variance(random)

    expected_mean = 1.0/lambda_
    expected_variance = expected_mean/lambda_

    str = (
        "Actual Mean:       %.10f\n"
        "Expected Mean:     %.10f\n"
        "Actual Variance:   %.10f\n"
        "Expected Variance: %.10f\n\n"
        "------------------------------------------------------\n"
    ) % (mean, expected_mean, variance, expected_variance)
    print(str)


class DES:
    __EVENT_OBSERVER = "Observer"
    __EVENT_ARRIVAL = "Arrival"
    __EVENT_DEPARTURE = "Departure"

    def __init__(self, packet_length_avg, trans_rate, sim_time, buffer_size, rho):
        self.__packet_length_avg = packet_length_avg
        self.__trans_rate = trans_rate
        self.__sim_time = sim_time
        self.__rho = rho
        self.__buffer_size = buffer_size
        self.__lambda = rho*trans_rate/packet_length_avg

    def __generate_packet_length(self):
        return generate_random(1.0/self.__packet_length_avg)

    def __calculate_service_time(self, packet_length):
        return packet_length/self.__trans_rate

    def __generate_observer_event_interval(self):
        return generate_random(self.__lambda * 5.0)

    def __generate_arrival_event_interval(self):
        return generate_random(self.__lambda)

    def __generate_observer_events(self):
        if __debug__:
            print("Generating Observer Events...\n")
            counter = 0

        observer_events = []
        current_time = 0.0

        while True:
            observer_event_interval = self.__generate_observer_event_interval()
            current_time += observer_event_interval

            if current_time <= self.__sim_time:
                observer_events.append((current_time, self.__EVENT_OBSERVER))

                if __debug__:
                    counter += 1
            else:
                if __debug__:
                    str = (
                        "Total Observer Events Generated: %d\n"
                        "Observer Events List Length:     %d\n"
                        "Total Observer Simulation Time:  %.10f\n"
                    ) % (counter, len(observer_events), current_time - observer_event_interval)
                    print(str)

                break
        return observer_events

    def __generate_arrival_events(self):
        if __debug__:
            print("Generating Arrival Events...\n")
            counter = 0

        arrival_events = []
        current_time = 0.0

        while True:
            arrival_event_interval = self.__generate_arrival_event_interval()
            current_time += arrival_event_interval

            if current_time <= self.__sim_time:
                arrival_events.append((current_time, self.__EVENT_ARRIVAL))

                if __debug__:
                    counter += 1
            else:
                if __debug__:
                    str = (
                        "Total Arrival Events Generated: %d\n"
                        "Arrival Events List Length:     %d\n"
                        "Total Arrival Simulation Time:  %.10f\n"
                    ) % (counter, len(arrival_events), current_time - arrival_event_interval)
                    print(str)

                break
        return arrival_events

    def __combine_generated_events(self, *events_list):
        if __debug__:
            print("Combining Generated Events...\n")

        combined_events = []

        for events in events_list:
            combined_events += events

        if __debug__:
            str = (
                "Combined Events List Length: %d\n"
            ) % (len(combined_events))
            print(str)

        return combined_events

    def __calculate_metrics(self, data):
        if __debug__:
            print("Calculating Metrics...\n")

        packets_in_queue_avg = statistics.mean(
            data["counter_packets_in_queue_list"])
        idle_time_proportion = data["counter_idle"] / \
            data["counter_observer"]
        packet_loss_probability = data["counter_dropped_packets"] / \
            data["counter_total_packets"]

        return {
            "buffer_size": self.__buffer_size,
            "rho": self.__rho,
            "packets_in_queue_avg": packets_in_queue_avg,
            "idle_time_proportion": idle_time_proportion,
            "packet_loss_probability": packet_loss_probability
        }

    def __process_events(self, events):
        if __debug__:
            print("Processing Events...\n")

        heapq.heapify(events)

        if __debug__:
            print("Heapified Events...\n")

        counter_arrvial = 0
        counter_departure = 0
        counter_observer = 0
        counter_idle = 0
        counter_dropped_packets = 0
        counter_total_packets = 0
        counter_packets_in_queue = 0
        counter_packets_in_queue_list = []
        latest_departure_time = 0.0

        while events:
            event = heapq.heappop(events)

            if event[1] == self.__EVENT_DEPARTURE:
                counter_departure += 1
                counter_packets_in_queue -= 1

                if __debug__:
                    if counter_packets_in_queue < 0:
                        print("Error: Negative Packets Counter!")
            elif event[1] == self.__EVENT_ARRIVAL:
                counter_total_packets += 1

                if counter_packets_in_queue < self.__buffer_size:
                    counter_arrvial += 1

                    packet_length = self.__generate_packet_length()
                    service_time = self.__calculate_service_time(packet_length)

                    departure_time = 0.0

                    if counter_packets_in_queue == 0:
                        departure_time = event[0] + service_time
                    else:
                        departure_time = max(
                            latest_departure_time, event[0]) + service_time

                    if __debug__:
                        if departure_time <= event[0] or departure_time <= latest_departure_time:
                            print("Error: Invalid Departure Time!")

                    latest_departure_time = departure_time

                    heapq.heappush(
                        events, (departure_time, self.__EVENT_DEPARTURE))

                    counter_packets_in_queue += 1
                else:
                    counter_dropped_packets += 1
            else:
                counter_observer += 1

                if counter_packets_in_queue == 0:
                    counter_idle += 1

                counter_packets_in_queue_list.append(counter_packets_in_queue)

        if __debug__:
            str = (
                "Arrival Counter:          %d\n"
                "Departure Counter:        %d\n"
                "Observer Counter:         %d\n"
                "Idle Counter:             %d\n"
                "Dropped Counter:          %d\n"
                "Total Packets Counter:    %d\n"
                "Packets in Queue Counter: %d\n"
                "List Counter Length:      %d\n"
                "Latest Departure Time:    %.10f\n"
            ) % (counter_arrvial, counter_departure, counter_observer, counter_idle, counter_dropped_packets, counter_total_packets, counter_packets_in_queue, len(counter_packets_in_queue_list), latest_departure_time)
            print(str)

        return {
            "counter_packets_in_queue_list": counter_packets_in_queue_list,
            "counter_idle": counter_idle,
            "counter_observer": counter_observer,
            "counter_dropped_packets": counter_dropped_packets,
            "counter_total_packets": counter_total_packets
        }

    def sim_MM1_queue(self):
        if self.__buffer_size == float("inf"):
            return self.sim_MM1K_queue()
        else:
            print("Error: Finite Buffer Size!\n")

    def sim_MM1K_queue(self):
        start_time = datetime.now().time()
        str = (
            "Simulation with\n"
            "Buffer Size: %s\n"
            "Rho:         %.10f\n"
            "Start Time: %s\n\n"
        ) % (self.__buffer_size, self.__rho, start_time)

        observer_events = self.__generate_observer_events()
        arrival_events = self.__generate_arrival_events()
        combined_events = self.__combine_generated_events(
            observer_events, arrival_events)
        data = self.__process_events(combined_events)
        metrics = self.__calculate_metrics(data)

        str += (
            "Packets in Queue Avg:    %.10f\n"
            "Idle Time Proportion:    %.10f\n"
            "Packet Loss Probability: %.10f\n\n"
        ) % (metrics["packets_in_queue_avg"], metrics["idle_time_proportion"], metrics["packet_loss_probability"])

        end_time = datetime.now().time()
        str += (
            "End Time: %s\n\n"
            "------------------------------------------------------\n"
        ) % (end_time)

        return [metrics, str]


def start_DES(lock, packet_length_avg, trans_rate, sim_time, buffer_size, rho):
    DES_instance = DES(packet_length_avg, trans_rate,
                       sim_time, buffer_size, rho)
    res = []

    if buffer_size == float("inf"):
        res = DES_instance.sim_MM1_queue()
    else:
        res = DES_instance.sim_MM1K_queue()

    lock.acquire()

    try:
        print(res[1])
    finally:
        lock.release()

    return res[0]


def main():
    start_time = time.time()

    verify_generated_random(75.0)

    packet_length_avg = 2000.0
    trans_rate = 1000000.0
    sim_time = 1000

    manager = Manager()
    lock = manager.Lock()
    pool = Pool(5)

    # infinite buffer size
    rho_list_inf = [0.25 + 0.1*i for i in range(8)] + [1.2]
    start_inf_DES = partial(start_DES, lock, packet_length_avg,
                            trans_rate, sim_time, float("inf"))

    pool.map(start_inf_DES, rho_list_inf)

    # finite buffer size
    buffer_size_list = [10, 25, 50]
    rho_list_finite = [0.5 + 0.1*i for i in range(11)]

    for buffer_size in buffer_size_list:
        start_finite_DES = partial(start_DES, lock, packet_length_avg,
                                   trans_rate, sim_time, buffer_size)

        pool.map(start_finite_DES, rho_list_finite)

    end_time = time.time()

    str = (
        "Execution Time: %s seconds\n"
    ) % (end_time - start_time)
    print(str)

    return


if __name__ == "__main__":
    main()
