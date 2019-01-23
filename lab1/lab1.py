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
    def __init__(self, packet_length, trans_rate, sim_time):
        self.__packet_length = packet_length
        self.__trans_rate = trans_rate
        self.__sim_time = sim_time

    def __generate_observer_event(self, lambda_):
        return Observer(generate_random(lambda_ * 5))

    def __generate_arrival_event(self, lambda_):
        return Arrival(generate_random(lambda_))

    def __generate_observer_events(self):
        return

    def __generate_arrival_events(self):
        return

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
