import bisect
import math
import random
import statistics
from datetime import datetime


def generate_random(lambda_):
    return -math.log(1.0 - random.uniform(0.0, 1.0))/lambda_


# Q1
def verify_generated_random(lambda_):
    random = [generate_random(lambda_) for i in range(1000)]

    mean = statistics.mean(random)
    variance = statistics.variance(random)

    expected_mean = 1.0/lambda_
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

        observer_events = []
        current_time = 0.0
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
                        "Total Observer Events Generated: %d\n"
                        "Observer Events List Length:     %d\n"
                        "Total Observer Simulation Time:  %f\n"
                    ) % (counter, len(observer_events), current_time - observer_event_interval)
                    print(str)

                break
        return observer_events

    def __generate_arrival_events(self):
        if __debug__:
            print("Generating Arrival Events...\n")

        arrival_events = []
        current_time = 0.0
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
                        "Total Arrival Events Generated: %d\n"
                        "Arrival Events List Length:     %d\n"
                        "Total Arrival Simulation Time:  %f\n"
                    ) % (counter, len(arrival_events), current_time - arrival_event_interval)
                    print(str)

                break
        return arrival_events

    def __sort_generated_events(self, *events_list):
        if __debug__:
            print("Sorting Generated Events...\n")

        combined_events = []

        for events in events_list:
            combined_events += events

        if __debug__:
            str = (
                "Combined Events List Length: %d\n"
            ) % (len(combined_events))
            print(str)

        return sorted(combined_events, key=lambda event: event.time, reverse=True)

    def __calculate_metrics(self, data):
        # TODO: time-average number of packets E[N], Proportion of idle Pidle
        if __debug__:
            print("Calculating Metrics...\n")
        pass

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
        latest_departure_time = 0.0

        events_time_list = [event.time for event in reversed(events)]

        while events:
            event = events.pop()
            del events_time_list[0]

            if isinstance(event, Departure):
                counter_departure += 1
                counter_packets_in_queue -= 1

                if __debug__:
                    if counter_packets_in_queue < 0:
                        print("Error: Negative Packets Counter!")
            elif isinstance(event, Arrival):
                counter_total_packets += 1

                if counter_packets_in_queue < self.__buffer_size:
                    packet_length = self.__generate_packet_length()
                    service_time = self.__calculate_service_time(packet_length)

                    departure_time = 0.0

                    if counter_packets_in_queue == 0:
                        departure_time = event.time + service_time
                    else:
                        departure_time = max(
                            latest_departure_time, event.time) + service_time

                    counter_arrvial += 1
                    counter_packets_in_queue += 1

                    if __debug__:
                        if departure_time <= event.time or departure_time <= latest_departure_time:
                            print("Error: Invalid Departure Time!")

                    latest_departure_time = departure_time

                    reversed_insertion_position = bisect.bisect(
                        events_time_list, departure_time)
                    insertion_position = -reversed_insertion_position

                    if __debug__:
                        if (
                            events[insertion_position].time != events_time_list[reversed_insertion_position] or
                            len(events) != len(events_time_list)
                        ):
                            str = (
                                "Error: Incorrect Mapping!\n"
                                "Event Time:            %f\n"
                                "Time in List:          %f\n"
                                "Insertion Position:    %d\n"
                                "Insertion Position(R): %d\n"
                                "Events Length:         %d\n"
                                "List Length:           %d\n"
                            ) % (events[insertion_position].time, events_time_list[reversed_insertion_position], insertion_position, reversed_insertion_position, len(events), len(events_time_list))
                            print(str)

                    events.insert(insertion_position,
                                  Departure(departure_time))
                    events_time_list.insert(
                        reversed_insertion_position, departure_time)
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
        verify_generated_random(75.0)

    packet_length_avg = 2000.0
    trans_rate = 1000000.0
    sim_time = 0.1

    # infinite buffer size
    rho_list_inf = [0.25 + 0.1*i for i in range(8)] + [1.2]

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
    buffer_size_list = [10, 25, 50]
    rho_list_finite = (
        [0.5 + 0.1*i for i in range(11)] +
        [0.4 + 0.1*i for i in range(17)] +
        [2 + 0.2*i for i in range(16)] +
        [5 + 0.4*i for i in range(13)]
    )

    for buffer_size in buffer_size_list:
        for rho in rho_list_finite:
            start_time = datetime.now().time()
            str = (
                "Simulation with\n"
                "Buffer Size: %d\n"
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
