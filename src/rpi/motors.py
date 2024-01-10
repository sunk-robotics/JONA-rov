#  import adafruit_motor.servo
from adafruit_servokit import ServoKit
import time


class Motors:
    def __init__(self):
        # After calibrating with the oscilloscope, the correct reference clock
        # speed for the particular PCA9685 should be 24.5 MHz, rather than the
        # standard 25 MHz. If the motors don't work for some reason, check the
        # reference clock.
        self.kit = ServoKit(channels=16, reference_clock_speed=24_500_000)
        self.num_motors = 8
        # a table that maps the motor number to the correct channel on the PWM
        # controller
        self.motor_channel_table = {
            0: 10,
            1: 9,
            2: 14,
            3: 12,
            4: 13,
            5: 8,
            6: 11,
            7: 15,
        }
        self.motor_velocities = [0, 0, 0, 0, 0, 0, 0, 0]
        self.speed_limit = 0.5
        # set the correct pulse range (1100 microseconds to 1900 microseconds)
        for motor_num in range(self.num_motors):
            self.kit.servo[self.motor_channel_table[motor_num]]\
                .set_pulse_width_range(1100, 1900)
        self.stop_all()
        # each motors needs to receive a neutral signal for at least two
        # seconds, otherwise they won't work
        time.sleep(2)

    def drive_motor(self, motor_num: int, velocity: float):
        # maps the velocity from -1..1 where -1 is full throttle reverse and
        # 1 is full throttle forward to an angle where 0 degrees is full
        # throttle reverse and 180 degrees is full throttle forward
        angle = int(velocity * 90) + 90
        # motor 0 has a shitty connection
        #  if motor_num == 0:
        #      return
        self.kit.servo[self.motor_channel_table[motor_num]].angle = angle

    # move the ROV left or right
    def calc_x_velocity(self, velocity: float):
        # positive velocity - ROV moves right
        # negative velocity - ROV moves left
        self.motor_velocities[0] -= velocity
        self.motor_velocities[1] += velocity
        self.motor_velocities[2] += velocity
        self.motor_velocities[3] -= velocity

    # move the ROV forward or backward
    def calc_y_velocity(self, velocity: float):
        # positive velocity - ROV moves forward
        # negative velocity - ROV moves backward
        self.motor_velocities[0] -= velocity
        self.motor_velocities[1] -= velocity
        self.motor_velocities[2] += velocity
        self.motor_velocities[3] += velocity

    # move the ROV up or down
    def calc_z_velocity(self, velocity: float):
        # positive velocity - ROV moves up
        # negative velocity - ROV moves down
        self.motor_velocities[4] += velocity
        self.motor_velocities[5] += velocity
        self.motor_velocities[6] += velocity
        self.motor_velocities[7] += velocity

    # turn the ROV left or right
    def calc_yaw_velocity(self, velocity: float):
        # positive velocity - ROV turns right
        # negative velocity - ROV turns left
        self.motor_velocities[0] -= velocity
        self.motor_velocities[1] += velocity
        self.motor_velocities[2] -= velocity
        self.motor_velocities[3] += velocity

    # make the ROV pitch upward or downward
    def calc_pitch_velocity(self, velocity: float):
        # positive velocity - ROV pitches up
        # negative velocity - ROV pitches down
        self.motor_velocities[4] += velocity
        self.motor_velocities[5] += velocity
        self.motor_velocities[6] -= velocity
        self.motor_velocities[7] -= velocity

    # make the ROV do a barrel roll
    def calc_roll_velocity(self, velocity: float):
        # positive velocity - ROV rolls to the right, maybe
        # negative velocity - ROV rolls to the left, maybe
        self.motor_velocities[4] -= velocity
        self.motor_velocities[5] += velocity
        self.motor_velocities[6] -= velocity
        self.motor_velocities[7] += velocity

    def stop_all(self):
        for motor_num in range(len(self.motor_velocities)):
            self.drive_motor(motor_num, 0)

    def drive_motors(self, x_velocity=0, y_velocity=0, z_velocity=0,
                     yaw_velocity=0, pitch_velocity=0, roll_velocity=0):
        # reset all the velocities to 0
        for i in range(len(self.motor_velocities)):
            self.motor_velocities[i] = 0

        self.calc_x_velocity(x_velocity)
        self.calc_y_velocity(y_velocity)
        self.calc_z_velocity(z_velocity)
        self.calc_yaw_velocity(yaw_velocity)
        self.calc_pitch_velocity(pitch_velocity)
        self.calc_roll_velocity(roll_velocity)

        for motor_num in range(len(self.motor_velocities)):
            if self.motor_velocities[motor_num] > self.speed_limit:
                self.motor_velocities[motor_num] = self.speed_limit
            elif self.motor_velocities[motor_num] < -self.speed_limit:
                self.motor_velocities[motor_num] = -self.speed_limit

        for motor_num, velocity in enumerate(self.motor_velocities):
            self.drive_motor(motor_num, velocity)

    def test_motors(self):
        for motor_num in range(self.num_motors):
            self.drive_motor(motor_num, 0.3)
            print(f"Testing motor: {motor_num}")
            time.sleep(2)
            self.drive_motor(motor_num, 0)
        self.stop_all()


def main():
    motors = Motors()
    motors.drive_motor(4, 0.3)
    #  motors.test_motors()
    #  motors.drive_motor(7, 0.15)
    time.sleep(5)
    motors.stop_all()
    #  motors.drive_motors(z_velocity=0.5)
    #  time.sleep(2)
    #  motors.drive_motors()


if __name__ == "__main__":
    main()

