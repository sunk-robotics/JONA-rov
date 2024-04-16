#!/usr/bin/python
import argparse
import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

#  from pprint import pprint


def five_day_max(sturgeon_data: list[int]) -> tuple[int, tuple[int]]:
    if len(sturgeon_data) < 5:
        return sum(sturgeon_data)
    five_day_max = 0
    day_range = (0, 0)
    for i in range(len(sturgeon_data) - 5):
        if sum(sturgeon_data[i : i + 5]) > five_day_max:
            five_day_max = sum(sturgeon_data[i : i + 5])
            day_range = (i + 1, i + 5)

    return five_day_max, day_range


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    target_file = Path(args.path)
    try:
        with open(target_file, mode="r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            sturgeon_data = []
            for row in csv_reader:
                sturgeon_data.append([int(i) for i in row])
    except FileNotFoundError:
        print(f"Error: Invalid path! The file '{args.path}' can't be found. Try again.")
        exit(1)

    best_receiver = 0
    sturgeon_count = 0
    day_range = (0, 0)
    for receiver_num, receiver_data in enumerate(sturgeon_data):
        if five_day_max(receiver_data)[0] > sturgeon_count:
            best_receiver = receiver_num + 1
            sturgeon_count, day_range = five_day_max(receiver_data)

    print(f"Potential Spawning Location: Receiver {best_receiver}")
    print(f"Day Range: Day {day_range[0]} - Day {day_range[1]}")

    fig, ax = plt.subplots()

    ax.set_title("Number of sturgeon detected at each receiver over time")
    ax.set_ylabel("Number of sturgeon")
    ax.set_xlim([1, 15])
    ax.set_xlabel("Time (day)")
    ax.plot(np.arange(15), sturgeon_data[0])

    ax.plot(sturgeon_data[0], linewidth=3.0, label="Receiver 1")
    ax.plot(sturgeon_data[1], linewidth=3.0, label="Receiver 2")
    ax.plot(sturgeon_data[2], linewidth=3.0, label="Receiver 3")
    ax.legend(loc="upper right")

    plt.text(
        0.5,
        -0.2,
        "Potential Spawning Location:",
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
        size=10,
    )

    if best_receiver == 1:
        receiver_text_color = "orange"
    elif best_receiver == 2:
        receiver_text_color = "green"
    else:
        receiver_text_color = "red"
    plt.text(
        0.5,
        -0.27,
        f"Receiver {best_receiver}",
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
        color=receiver_text_color,
        size=10,
    )
    plt.text(
        0.5,
        -0.34,
        f"Day {day_range[0]} - Day {day_range[1]}",
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
        color=receiver_text_color,
        size=10,
    )
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
