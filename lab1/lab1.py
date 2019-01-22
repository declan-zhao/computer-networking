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


def main():
    # TODO: main
    verify_generated_random(75)
    return


if __name__ == "__main__":
    main()
