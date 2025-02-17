import sys
from collections import deque
import os


class Process:

    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start_time = -1
        self.completion_time = -1
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1


def parse_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]

    processes = []
    total_runtime = 0
    algorithm = ""
    quantum = None
    num_processes = None

    for line in lines:
        parts = line.split()
        if not parts:
            continue

        if parts[0] == "processcount":
            num_processes = int(parts[1])
        elif parts[0] == "runfor":
            total_runtime = int(parts[1])
        elif parts[0] == "use":
            algorithm = parts[1]
        elif parts[0] == "quantum":
            quantum = int(parts[1])
        elif parts[0] == "process":
            name = parts[2]
            arrival = int(parts[4])
            burst = int(parts[6])
            processes.append(Process(name, arrival, burst))
        elif parts[0] == "end":
            break

    if not num_processes:
        print("Error: Missing parameter processcount")
        sys.exit(1)
    if not total_runtime:
        print("Error: Missing parameter runfor")
        sys.exit(1)
    if not algorithm:
        print("Error: Missing parameter use")
        sys.exit(1)
    if algorithm == "rr" and quantum is None:
        print("Error: Missing quantum parameter when use is 'rr'")
        sys.exit(1)

    return processes, total_runtime, algorithm, quantum


def fcfs_scheduling(processes, total_runtime):
    processes.sort(key=lambda p: p.arrival)
    current_time = 0
    event_log = []

    event_log.append(f"{len(processes)} processes")
    event_log.append("Using First-Come First-Served")

    for process in processes:
        # Idle until the process arrives
        while current_time < process.arrival:
            event_log.append(f"Time {current_time:3d} : Idle")
            current_time += 1

        # Log process arrival
        event_log.append(f"Time {current_time:3d} : {process.name} arrived")
        # Log process selection with formatted burst
        event_log.append(f"Time {current_time:3d} : {process.name} selected (burst {process.burst:3d})")

        process.start_time = current_time
        process.response_time = current_time - process.arrival
        current_time += process.burst
        process.completion_time = current_time
        process.turnaround_time = process.completion_time - process.arrival
        process.waiting_time = process.turnaround_time - process.burst

        event_log.append(f"Time {current_time:3d} : {process.name} finished")

    # Log any remaining idle time until total_runtime
    while current_time < total_runtime:
        event_log.append(f"Time {current_time:3d} : Idle")
        current_time += 1

    event_log.append(f"Finished at time {total_runtime:3d}")

    # Log process summary info
    for process in processes:
        event_log.append(
            f"{process.name} wait {process.waiting_time:3d} turnaround {process.turnaround_time:3d} response {process.response_time:3d}"
        )

    return event_log


def preemptive_sjf_scheduling(processes, total_runtime):
    processes.sort(key=lambda p: (p.arrival, p.burst))
    ready_queue = []
    current_time = 0
    event_log = []
    remaining_processes = processes[:]
    active_process = None

    event_log.append(f"{len(processes)} processes")
    event_log.append("Using preemptive Shortest Job First")

    while current_time < total_runtime:
        # Add new arrivals to the ready queue
        for process in remaining_processes[:]:
            if process.arrival == current_time:
                event_log.append(f"Time {current_time} : {process.name} arrived")
                ready_queue.append(process)
                remaining_processes.remove(process)

        # Check if active process is finished
        if active_process and active_process.remaining <= 0:
            event_log.append(f"Time {current_time} : {active_process.name} finished")
            active_process.completion_time = current_time
            active_process = None

        # If there is a process waiting with a shorter remaining time, preempt the active process
        if ready_queue:
            ready_queue.sort(key=lambda p: p.remaining)
            if active_process:
                if active_process.remaining > ready_queue[0].remaining:
                    # Preempt active process: re-queue it and select the new process
                    ready_queue.append(active_process)
                    active_process = ready_queue.pop(0)
                    if active_process.response_time == -1:
                        active_process.response_time = current_time - active_process.arrival
                    event_log.append(
                        f"Time {current_time} : {active_process.name} selected (burst {active_process.remaining})"
                    )
            else:
                active_process = ready_queue.pop(0)
                if active_process.response_time == -1:
                    active_process.response_time = current_time - active_process.arrival
                event_log.append(
                    f"Time {current_time} : {active_process.name} selected (burst {active_process.remaining})"
                )

        # If there is an active process, run it for 1 time unit
        if active_process:
            active_process.remaining -= 1
        else:
            event_log.append(f"Time {current_time} : Idle")

        current_time += 1

    event_log.append(f"Finished at time {total_runtime}")

    unfinished_processes = [p.name for p in processes if p.remaining > 0]
    if unfinished_processes:
        event_log.append("Unfinished processes: " + " ".join(unfinished_processes))

    for process in processes:
        # If a process never finished, mark its completion time at total_runtime
        if process.completion_time == -1:
            process.completion_time = total_runtime
        process.turnaround_time = process.completion_time - process.arrival
        process.waiting_time = process.turnaround_time - process.burst
        event_log.append(
            f"{process.name} wait {process.waiting_time} turnaround {process.turnaround_time} response {process.response_time}"
        )

    return event_log


def round_robin_scheduling(processes, total_runtime, quantum):
    processes.sort(key=lambda p: p.arrival)
    queue = deque()
    current_time = 0
    event_log = []
    remaining_processes = processes[:]

    event_log.append(f"{len(processes)} processes")
    event_log.append("Using Round Robin")
    event_log.append(f"Quantum {quantum}")

    while current_time < total_runtime:
        for process in remaining_processes[:]:
            if process.arrival <= current_time:
                queue.append(process)
                remaining_processes.remove(process)

        if queue:
            process = queue.popleft()
            if process.response_time == -1:
                process.response_time = current_time - process.arrival
            time_slice = min(process.remaining, quantum)
            event_log.append(
                f"Time {current_time} : {process.name} selected (burst {process.remaining})"
            )
            process.remaining -= time_slice
            current_time += time_slice
            if process.remaining > 0:
                queue.append(process)
            else:
                process.completion_time = current_time
                event_log.append(
                    f"Time {current_time} : {process.name} finished")
        else:
            event_log.append(f"Time {current_time} : Idle")
            current_time += 1

    event_log.append(f"Finished at time {total_runtime}")

    unfinished_processes = [p.name for p in processes if p.remaining > 0]
    if unfinished_processes:
        event_log.append("Unfinished processes: " +
                         " ".join(unfinished_processes))

    for process in processes:
        process.turnaround_time = process.completion_time - process.arrival
        process.waiting_time = process.turnaround_time - process.burst
        event_log.append(
            f"{process.name} wait {process.waiting_time} turnaround {process.turnaround_time} response {process.response_time}"
        )

    return event_log


def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-get.py <input file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not input_file.endswith(".in"):
        print("Error: Input file must have '.in' extension")
        sys.exit(1)

    output_file = input_file.replace(".in", ".out")
    processes, total_runtime, algorithm, quantum = parse_input(input_file)

    if algorithm == "sjf":
        event_log = preemptive_sjf_scheduling(processes, total_runtime)
    elif algorithm == "fcfs":
        event_log = fcfs_scheduling(processes, total_runtime)
    elif algorithm == "rr":
        event_log = round_robin_scheduling(processes, total_runtime, quantum)
    else:
        print(f"Error: Unsupported algorithm {algorithm}.")
        sys.exit(1)

    with open(output_file, 'w') as file:
        file.write("\n".join(event_log) + "\n")


if __name__ == "__main__":
    main()
