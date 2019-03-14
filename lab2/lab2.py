import csv
import math
import random
import time
from collections import deque
from datetime import datetime
from multiprocessing import Manager, Pool


# packets generator
class PacketsGenerator:
    def __init__(self, arrival_rate_avg, sim_time):
        self.__arrival_rate_avg = arrival_rate_avg
        self.__sim_time = sim_time

    @staticmethod
    def __generate_poisson_random(lambda_):
        return -math.log(1.0 - random.random())/lambda_

    def generate_packets(self):
        packets = deque()
        current_time = 0.0

        while True:
            arrival_interval = self.__generate_poisson_random(
                self.__arrival_rate_avg)
            current_time += arrival_interval

            if current_time < self.__sim_time:
                packets.append(current_time)
            else:
                break

        return packets


# node
class Node:
    __BACKOFF_MAX = 10

    def __init__(self, id, packets, trans_rate, trans_delay, prop_delay, is_persistent):
        self.__id = id
        self.__packets = packets
        self.__trans_rate = trans_rate
        self.__trans_delay = trans_delay
        self.__prop_delay = prop_delay
        self.__is_persistent = is_persistent
        self.__collision_counter = 0
        self.__wait_counter = 0
        self.__updated_arrival_time = -1.0

    @staticmethod
    def __generate_backoff_random(k):
        return random.randint(0, 2**k - 1)

    def __calculate_collision_backoff_time(self):
        self.__collision_counter += 1

        if self.__collision_counter > Node.__BACKOFF_MAX:
            self.__pop_and_reset()

            return None

        r = Node.__generate_backoff_random(self.__collision_counter)
        backoff_interval = r * 512 / self.__trans_rate

        return backoff_interval

    def __calculate_wait_backoff_time(self):
        if self.__wait_counter < Node.__BACKOFF_MAX:
            self.__wait_counter += 1

        r = Node.__generate_backoff_random(self.__wait_counter)
        backoff_interval = r * 512 / self.__trans_rate

        return backoff_interval

    def __pop_and_reset(self):
        self.__reset_collision_counter()
        self.__popleft_packet()

    def __popleft_packet(self):
        return self.__packets.popleft()

    def __reset_collision_counter(self):
        self.__collision_counter = 0

    def __reset_wait_counter(self):
        self.__wait_counter = 0

    def __calculate_total_prop_delay(self, node_id):
        return abs(self.__id - node_id) * self.__prop_delay

    def reschedule_busy_bus(self, node_id, current_sim_time):
        total_prop_delay = self.__calculate_total_prop_delay(node_id)
        busy_start_time = current_sim_time + total_prop_delay
        busy_end_time = busy_start_time + self.__trans_delay

        # reschedule arrival time
        if self.__is_persistent or self.__id == node_id:
            # persistent mode or sender node
            self.__updated_arrival_time = max(
                self.updated_first_packet_arrival_time, busy_end_time)
        else:
            # non-persistent mode and not sender node
            while True:
                if self.updated_first_packet_arrival_time < busy_end_time:
                    backoff_interval = self.__calculate_wait_backoff_time()
                    self.__updated_arrival_time = self.updated_first_packet_arrival_time + backoff_interval
                else:
                    self.__reset_wait_counter()
                    break

    def check_collision(self, node_id, current_sim_time):
        is_colliding = False

        total_prop_delay = self.__calculate_total_prop_delay(node_id)
        collision_start_time = current_sim_time
        collision_end_time = collision_start_time + total_prop_delay

        if self.updated_first_packet_arrival_time <= collision_end_time:
            # collision
            is_colliding = True

        return is_colliding

    def reschedule_collision(self):
        backoff_interval = self.__calculate_collision_backoff_time()

        if backoff_interval is not None:
            # reschedule arrival time
            self.__updated_arrival_time = self.updated_first_packet_arrival_time + backoff_interval

    def transmission_success(self):
        self.__pop_and_reset()

    @property
    def id(self):
        return self.__id

    @property
    def updated_first_packet_arrival_time(self):
        return max(self.__updated_arrival_time, self.__packets[0]) if len(self.__packets) > 0 else float("inf")


# simulator
class DES:
    def __init__(self, node_num, arrival_rate_avg, trans_rate, packet_length, node_distance, prop_speed, sim_time, is_persistent):
        self.__node_num = node_num
        self.__arrival_rate_avg = arrival_rate_avg
        self.__trans_rate = trans_rate
        self.__packet_length = packet_length
        self.__trans_delay = packet_length/trans_rate
        self.__prop_delay = node_distance/prop_speed
        self.__sim_time = sim_time
        self.__is_persistent = is_persistent

    def __generate_nodes(self):
        pg = PacketsGenerator(self.__arrival_rate_avg, self.__sim_time)

        return [Node(k, pg.generate_packets(), self.__trans_rate, self.__trans_delay, self.__prop_delay, self.__is_persistent) for k in range(self.__node_num)]

    def __calculate_metrics(self, data):
        efficiency = data["successful_transmission_counter"] / \
            data["total_transmission_counter"]
        throughput = data["successful_transmission_counter"] * \
            data["packet_length"] / (data["sim_time"] * 10**6)

        return {
            "is_persistent": self.__is_persistent,
            "arrival_rate_avg": self.__arrival_rate_avg,
            "node_num": self.__node_num,
            "efficiency": efficiency,
            "throughput": throughput
        }

    def __process_events(self):
        # counter
        total_transmission_counter = 0
        successful_transmission_counter = 0

        # generate nodes
        nodes = self.__generate_nodes()

        current_sim_time = 0

        while True:
            # find the node to transmit
            sender_node = min(
                nodes, key=lambda n: n.updated_first_packet_arrival_time)
            # set current sim time
            current_sim_time = sender_node.updated_first_packet_arrival_time

            if current_sim_time >= self.__sim_time:
                break

            # start transmission
            total_transmission_counter += 1

            # detect and handle collision
            is_colliding = False

            for node in nodes:
                if node.id != sender_node.id:
                    is_node_colliding = node.check_collision(
                        sender_node.id, current_sim_time)

                    if is_node_colliding:
                        is_colliding = True
                        total_transmission_counter += 1
                        node.reschedule_collision()

            if is_colliding:
                sender_node.reschedule_collision()
            else:
                # no collision
                successful_transmission_counter += 1
                sender_node.transmission_success()

                for node in nodes:
                    node.reschedule_busy_bus(
                        sender_node.id, current_sim_time)

        return {
            "successful_transmission_counter": successful_transmission_counter,
            "total_transmission_counter": total_transmission_counter,
            "packet_length": self.__packet_length,
            "sim_time": self.__sim_time
        }

    def sim(self):
        start_time = datetime.now().time()
        str = (
            "Simulation with\n"
            "Persistent Mode:    %s\n"
            "Arrival Rate Avg:   %s\n"
            "Number of Nodes:    %s\n\n"
            "Start Time:         %s\n\n"
        ) % (self.__is_persistent, self.__arrival_rate_avg, self.__node_num, start_time)

        data = self.__process_events()
        metrics = self.__calculate_metrics(data)

        str += (
            "CSMA/CD Efficiency: %.10f\n"
            "CSMA/CD Throughput: %.10f Mbps\n\n"
        ) % (metrics["efficiency"], metrics["throughput"])

        end_time = datetime.now().time()
        str += (
            "End Time:           %s\n\n"
            "------------------------------------------------------\n"
        ) % (end_time)

        return [metrics, str]


def start_DES(lock, node_num, arrival_rate_avg, trans_rate, packet_length, node_distance, prop_speed, sim_time, is_persistent):
    DES_instance = DES(node_num, arrival_rate_avg, trans_rate,
                       packet_length, node_distance, prop_speed, sim_time, is_persistent)
    res = DES_instance.sim()

    lock.acquire()

    try:
        print(res[1])
    finally:
        lock.release()

    return res[0]


def write_to_csv(fields, headers, rows):
    timestamp = time.time() * 1000
    filename = ("lab2_output_%s.csv") % (round(timestamp))

    with open(filename, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fields)
        csvwriter.writerow(headers)
        csvwriter.writerows(rows)

    str = (
        "Created CSV File %s\n\n"
        "------------------------------------------------------\n"
    ) % (filename)
    print(str)


def main():
    start_time = time.time()

    trans_rate = float(1*10**6)
    packet_length = 1500.0
    node_distance = 10.0
    prop_speed = float(2*10**8)
    sim_time = 1000.0

    manager = Manager()
    lock = manager.Lock()
    pool = Pool(8)

    fields = [
        "is_persistent",
        "arrival_rate_avg",
        "node_num",
        "efficiency",
        "throughput"
    ]
    headers = {
        "is_persistent": "Persistent Mode",
        "arrival_rate_avg": "Average Arrival Rate (packets/s)",
        "node_num": "Number of Nodes",
        "efficiency": "CSMA/CD Efficiency",
        "throughput": "CSMA/CD Throughput (Mbps)"
    }

    node_num_list = [20 * (5 - k) for k in range(5)]
    arrival_rate_avg_list = [20, 10, 7]

    params_list = [(lock, node_num, arrival_rate_avg, trans_rate, packet_length, node_distance, prop_speed, sim_time, is_persistent)
                   for node_num in node_num_list for arrival_rate_avg in arrival_rate_avg_list for is_persistent in [True, False]]

    async_result = pool.starmap_async(start_DES, params_list)

    pool.close()
    pool.join()

    rows = sorted(async_result.get(), key=lambda row: (
        -row["is_persistent"], row["arrival_rate_avg"], row["node_num"]))

    write_to_csv(fields, headers, rows)

    end_time = time.time()

    str = (
        "Execution Time: %s seconds\n\n"
        "------------------------------------------------------\n"
    ) % (end_time - start_time)
    print(str)

    return


if __name__ == "__main__":
    main()
