from typing import Callable
from time import time

class PID:
    total: float = 0 # rolling sum/integral
    time: float = 0 # time

    prev_err: float = 0 # previous error
    curr_err: float = 0 # current error 

    def __init__(self, p: float, i: float, d: float, target: float, data_fn: Callable[[], float]):
        self.p_gain = p # proportional gain
        self.i_gain = i # integral gain
        self.d_gain = d # derivative gain
        self.data_fn = data_fn
        self.target = target # target position

    def calc_pid(self) -> float: # returns the PID calculation
        curr_time = time()
        d_time = curr_time - self.time
        self.time = curr_time
        state = self.data_fn() # current value, ie position, angle, etc

        self.total += state # adds to the integral

        self.prev_err = self.curr_err # moves forward in time
        self.curr_err = self.target - state # calculates the new error
        change = (self.curr_err - self.prev_err) / d_time # calculates the derivative

        return self.p_gain * self.curr_err + self.i_gain * self.total + self.d_gain * change # PID value
    




    