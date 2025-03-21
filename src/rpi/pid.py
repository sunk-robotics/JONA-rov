import math
import time


# used to adjust the motor velocities to keep the ROV at a constant position
class PID:
    def __init__(
        self,
        set_point=0,
        proportional_gain=0,
        integral_gain=0,
        derivative_gain=0,
    ):
        self.set_point = set_point
        self.proportional_gain = proportional_gain
        self.integral_gain = integral_gain
        self.derivative_gain = derivative_gain

        self.integral = 0
        self.last_time = time.time()
        self.last_error = set_point

    def compute(self, process_value):
        current_time = time.time()
        d_time = time.time() - self.last_time
        self.last_time = current_time

        # difference between the target value and measured value
        error = self.set_point - process_value
        # compute the integral ∫e(t) dt
        self.integral += error * d_time
        # compute the derivative de/dt
        d_error = (error - self.last_error) / d_time
        self.last_error = error

        # add the P, I, and the D together
        output = (
            self.proportional_gain * error
            + self.integral_gain * self.integral
            + self.derivative_gain * d_error
        )
        return output

    def update_set_point(self, set_point):
        self.set_point = set_point
        self.integral = 0
        self.last_time = time.time()
        self.last_error = set_point


class RotationalPID(PID):
    def compute(self, angle):
        current_time = time.time()
        d_time = time.time() - self.last_time
        self.last_time = current_time

        # find the signed smallest difference between the angles
        error = angle_between(self.set_point, angle)
        # compute the integral ∫e(t) dt
        self.integral += error * d_time
        # compute the derivative
        d_error = (error - self.last_error) / d_time
        self.last_error = error

        # add the P, I, and the D together
        output = (
            self.proportional_gain * error
            + self.integral_gain * self.integral
            + self.derivative_gain * d_error
        )
        return output


def angle_between(x, y):
    a = (x - y) % 360
    b = (y - x) % 360
    return a if a < b else -b


def main():
    #  print(90 - 100)
    print(angle_between(-30, -60))


if __name__ == "__main__":
    main()
