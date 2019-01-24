import math
import random
import statistics
from datetime import datetime


def generate_random(lambda_):
    return -math.log(1 - random.uniform(0, 1))/lambda_


# Q1
def verify_generated_random(lambda_):
    random = [generate_random(lambda_) for i in range(1000)]

    mean = statistics.mean(random)
    variance = statistics.variance(random)

    expected_mean = 1/lambda_
    expected_variance = expected_mean/lambda_

    str = (
        "Actual Mean:       %f\n"
        "Expected Mean:     %f\n"
        "Actual Variance:   %f\n"
        "Expected Variance: %f\n"
    ) % (mean, expected_mean, variance, expected_variance)
    print(str)


class Observer:
    def __init__(self, time):
        self.time = time


class Arrival:
    def __init__(self, time):
        self.time = time


class Departure:
    def __init__(self, time):
        self.time = time


class DES:
    def __init__(self, packet_length_avg, trans_rate, sim_time, rho, buffer_size=float("inf")):
        self.__packet_length_avg = packet_length_avg
        self.__trans_rate = trans_rate
        self.__sim_time = sim_time
        self.__rho = rho
        self.__buffer_size = buffer_size
        self.__lambda = rho*trans_rate/packet_length_avg

    def __generate_packet_length(self):
        return generate_random(1/self.__packet_length_avg)

    def __calculate_service_time(self, packet_length):
        return packet_length/self.__trans_rate

    def __generate_observer_event_interval(self):
        return generate_random(self.__lambda * 5)

    def __generate_arrival_event_interval(self):
        return generate_random(self.__lambda)

    def __generate_observer_events(self):
        if __debug__:
            print("Generating Observer Events...\n")

        observer_events = []
        current_time = 0
        counter = 0

        while True:
            observer_event_interval = self.__generate_observer_event_interval()
            current_time += observer_event_interval

            if current_time <= self.__sim_time:
                observer_events.append(Observer(current_time))
                counter += 1
            else:
                if __debug__:
                    str = (
                        "Total Observer Events Generated: %f\n"
                        "Observer Events List Length:     %f\n"
                        "Total Observer Simulation Time:  %f\n"
                    ) % (counter, len(observer_events), current_time - observer_event_interval)
                    print(str)

                break
        return observer_events

    def __generate_arrival_events(self):
        if __debug__:
            print("Generating Arrival Events...\n")

        arrival_events = []
        current_time = 0
        counter = 0

        while True:
            arrival_event_interval = self.__generate_arrival_event_interval()
            current_time += arrival_event_interval

            if current_time <= self.__sim_time:
                arrival_events.append(Arrival(current_time))
                counter += 1
            else:
                if __debug__:
                    str = (
                        "Total Arrival Events Generated: %f\n"
                        "Arrival Events List Length:     %f\n"
                        "Total Arrival Simulation Time:  %f\n"
                    ) % (counter, len(arrival_events), current_time - arrival_event_interval)
                    print(str)

                break
        return arrival_events

    def __sort_generated_events(self, observer_events, arrival_events):
        if __debug__:
            print("Sorting Generated Events...\n")

        combined_events = observer_events + arrival_events

        return sorted(combined_events, key=lambda event: event.time, reverse=True)

    def __search_insertion_position(self):
        return

    def __insert_departure_event(self):
        return

    def __calculate_metrics(self, data):
        # TODO: time-average number of packets E[N], Proportion of idle Pidle
        if __debug__:
            print("Calculating Metrics...\n")
        return

    def __process_events(self, events):
        if __debug__:
            print("Processing Events...\n")

        counter_arrvial = 0
        counter_departure = 0
        counter_observer = 0
        counter_idle = 0
        counter_dropped_packets = 0
        counter_total_packets = 0
        counter_packets_in_queue = 0
        counter_packets_in_queue_list = []
        latest_departure_time = 0

        for event in reversed(events):
            if isinstance(event, Departure):
                counter_departure += 1
                counter_packets_in_queue -= 1
            elif isinstance(event, Arrival):
                counter_total_packets += 1

                if counter_packets_in_queue < self.__buffer_size:
                    counter_arrvial += 1
                    counter_packets_in_queue += 1

                    packet_length = self.__generate_packet_length()
                    service_time = self.__calculate_service_time(packet_length)
                else:
                    counter_dropped_packets += 1
            else:
                counter_observer += 1

                if counter_packets_in_queue == 0:
                    counter_idle += 1

                counter_packets_in_queue_list.append(counter_packets_in_queue)

            events.pop()

        if __debug__:
            str = (
                "Arrival Counter:          %f\n"
                "Departure Counter:        %f\n"
                "Observer Counter:         %f\n"
                "Idle Counter:             %f\n"
                "Dropped Counter:          %f\n"
                "Total Packets Counter:    %f\n"
                "Packets in Queue Counter: %f\n"
                "List Counter Length:      %f\n"
                "Latest Departure Time:    %f\n"
            ) % (counter_arrvial, counter_departure, counter_observer, counter_idle, counter_dropped_packets, counter_total_packets, counter_packets_in_queue, len(counter_packets_in_queue_list), latest_departure_time)
            print(str)

        return [counter_arrvial, counter_departure, counter_observer, counter_idle, counter_dropped_packets, counter_total_packets, counter_packets_in_queue, counter_packets_in_queue_list, latest_departure_time]

    def sim_MM1_queue(self):
        if self.__buffer_size == float("inf"):
            self.sim_MM1K_queue()
        else:
            print("Error: Finite Buffer Size!\n")

    def sim_MM1K_queue(self):
        observer_events = self.__generate_observer_events()
        arrival_events = self.__generate_arrival_events()
        sorted_events = self.__sort_generated_events(
            observer_events, arrival_events)
        data = self.__process_events(sorted_events)
        self.__calculate_metrics(data)


def main():
    if __debug__:
        verify_generated_random(75)

    packet_length_avg = 2000
    trans_rate = 1000000
    sim_time = 1000

    # infinite buffer size
    rho_list_inf = [0.5]

    for rho in rho_list_inf:
        start_time = datetime.now().time()
        str = (
            "Simulation with\n"
            "Infinite Buffer Size\n"
            "Rho: %f\n"
            "Running, Start Time: %s\n"
        ) % (rho, start_time)
        print(str)

        DES_inf = DES(packet_length_avg, trans_rate, sim_time, rho)
        DES_inf.sim_MM1_queue()

        end_time = datetime.now().time()
        str = (
            "Complete, End Time: %s\n\n"
        ) % (end_time)
        print(str)

    # finite buffer size
    buffer_size_list = [10]
    rho_list_finite = [0.5]

    for buffer_size in buffer_size_list:
        for rho in rho_list_finite:
            start_time = datetime.now().time()
            str = (
                "Simulation with\n"
                "Buffer Size: %f\n"
                "Rho:         %f\n"
                "Running, Start Time: %s\n"
            ) % (buffer_size, rho, start_time)
            print(str)

            DES_finite = DES(packet_length_avg, trans_rate,
                             sim_time, rho, buffer_size)
            DES_finite.sim_MM1K_queue()

            end_time = datetime.now().time()
            str = (
                "Complete, End Time: %s\n\n"
            ) % (end_time)
            print(str)

    return


if __name__ == "__main__":
    main()
