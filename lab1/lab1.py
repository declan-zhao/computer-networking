import math
import random
import statistics


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
    def __init__(self, packet_length_lambda, trans_rate, sim_time):
        self.__packet_length_lambda = packet_length_lambda
        self.__trans_rate = trans_rate
        self.__sim_time = sim_time

    def __generate_observer_event(self, lambda_):
        return Observer(generate_random(lambda_ * 5))

    def __generate_arrival_event(self, lambda_):
        return Arrival(generate_random(lambda_))

    def __generate_observer_events(self, lambda_):
        observer_events = []
        current_time = 0

        while(True):
            if current_time <= self.__sim_time:
                observer_event = self.__generate_observer_event(lambda_)
                current_time += observer_event.time
                observer_events.append(observer_event)
            else:
                break
        return observer_events

    def __generate_arrival_events(self, lambda_):
        arrival_events = []
        current_time = 0

        while(True):
            if current_time <= self.__sim_time:
                arrival_event = self.__generate_arrival_event(lambda_)
                current_time += arrival_event.time
                arrival_events.append(arrival_event)
            else:
                break
        return arrival_events

    def __sort_generated_events(self, observer_events, arrival_events):
        return observer_events.append(arrival_events).sort(key=lambda event: event.time)

    def sim_MM1_queue(self):
        return

    def sim_MM1K_queue(self):
        return


def main():
    # TODO: main
    verify_generated_random(75)
    return


if __name__ == "__main__":
    main()
