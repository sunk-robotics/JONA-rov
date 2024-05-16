from time import time, sleep


class Timer:
    def __init__(self):
        self.elapsed_time = 0
        self.start_time = 0
        self.stopped = True

    def start(self):
        if self.stopped:
            self.start_time = time()
        self.stopped = False

    def stop(self) -> float:
        self.elapsed_time += time() - self.start_time
        self.stopped = True
        return self.elapsed_time

    def read(self) -> float:
        if not self.stopped:
            return self.elapsed_time + time() - self.start_time
        else:
            return self.elapsed_time

    def reset(self):
        self.elapsed_time = 0
        self.start_time = 0

    def restart(self):
        self.elapsed_time = 0
        self.start_time = 0
        self.stopped = False


def main():
    timer = Timer()

    timer.start()
    sleep(2)
    print(timer.read())
    print(timer.stop())
    sleep(1)
    timer.start()
    sleep(2)
    print(timer.read())


if __name__ == "__main__":
    main()
