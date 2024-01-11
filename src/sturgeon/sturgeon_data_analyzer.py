import csv
import math
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint

def five_day_max(sturgeon_data: list[int]) -> tuple[int, tuple[int]]:
    if len(sturgeon_data) < 5:
        return sum(sturgeon_data)
    five_day_max = 0
    day_range = 
    for i in range(len(sturgeon_data) - 5):
        if sum(sturgeon_data[i:i + 5]) > five_day_max:
            five_day_max = sum(sturgeon_data[i:i + 5])

    return five_day_max


def main():
    with open("sturgeon_data.csv", mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        sturgeon_data = []
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            sturgeon_data.append([int(i) for i in row])

    best_receiver = 0
    sturgeon_count = 0
    day_range = (0, 0)
    for receiver_num, receiver_data in enumerate(sturgeon_data):
        if five_day_max(receiver_data) > sturgeon_count:
            best_receiver = receiver_num + 1
            sturgeon_count = five_day_max(receiver_data)
            day_range = ()

    print(f"Potential Spawning Location: Receiver {best_receiver}")

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
    plt.show()
    #  np.random.seed(42)


    #  rng = np.arange(50)
    #  rnd = np.random.randint(0, 10, size=(3, rng.size))
    #  yrs = 1950 + rng

    #  fig, ax = plt.subplots(figsize=(5, 3))
    #  ax.stackplot(yrs, rng + rnd, labels=["Eastasia", "Eurasia", "Oceania"])
    #  ax.set_title("Combined debt growth over time")
    #  ax.legend(loc="upper left")
    #  ax.set_ylabel("Total debt")
    #  ax.set_xlim(xmin=yrs[0], xmax=yrs[-1])
    #  fig.tight_layout()
    #  plt.show()


if __name__ == "__main__":
    main()
