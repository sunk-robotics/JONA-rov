from adafruit_servokit import ServoKit
import math
from orientation import cartesian_to_spherical
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
            0: 12,
            1: 13,
            2: 8,
            3: 10,
            4: 9,
            5: 14,
            6: 15,
            7: 11,
        }
        self.motor_velocities = [0, 0, 0, 0, 0, 0, 0, 0]
        self.speed_limit = 1
        # set the correct pulse range (1100 microseconds to 1900 microseconds)
        for motor_num in range(self.num_motors):
            self.kit.servo[self.motor_channel_table[motor_num]].set_pulse_width_range(
                1100, 1900
            )
        self.stop_all()
        # each motors needs to receive a neutral signal for at least two
        # seconds, otherwise they won't work
        time.sleep(2)

    def drive_motor(self, motor_num: int, velocity: float):
        # maps the velocity from -1..1 where -1 is full throttle reverse and
        # 1 is full throttle forward to an angle where 0 degrees is full
        # throttle reverse and 180 degrees is full throttle forward
        angle = int(velocity * 90) + 90
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

    def drive_motors(
        self,
        x_velocity=0,
        y_velocity=0,
        z_velocity=0,
        yaw_velocity=0,
        pitch_velocity=0,
        roll_velocity=0,
    ):
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

    def find_max_speed(self, z_rotate, x_rotate) -> (float, float, float):
        SLOPE = math.sqrt(3)
        x_coord = 0
        y_coord = 0
        z_coord = 0

        z_rotate = math.radians(z_rotate)
        x_rotate = math.radians(x_rotate)

        # find max x and y speed on horizontal plane
        if math.degrees(z_rotate) < 90:
            x_coord = (SLOPE * 2) / (math.tan(z_rotate) + SLOPE)
            y_coord = -SLOPE * (x_coord) + (SLOPE * 2)

        elif math.degrees(z_rotate) < 180:
            x_coord = (SLOPE * 2) / (math.tan(z_rotate) - SLOPE)
            y_coord = SLOPE * (x_coord) + (SLOPE * 2)

        elif math.degrees(z_rotate) < 270:
            x_coord = -(SLOPE * 2) / (math.tan(z_rotate) + SLOPE)
            y_coord = -SLOPE * (x_coord) - (SLOPE * 2)

        elif math.degrees(z_rotate) < 360:
            x_coord = -(SLOPE * 2) / (math.tan(z_rotate) - SLOPE)
            y_coord = SLOPE * (x_coord) - (SLOPE * 2)

        xy_dist = math.sqrt(y_coord**2 + x_coord**2)

        # max angle before hitting ceiling
        max_x_rotate = math.atan((4 / xy_dist))

        # check if x_rotate hits ceiling
        if (
            x_rotate < max_x_rotate
            or (
                x_rotate > math.radians(180) - max_x_rotate
                and x_rotate < math.radians(180) + max_x_rotate
            )
            or x_rotate > math.radians(270) + max_x_rotate
        ):
            # if it doesn't, find z_coord according to x_rotate and xy_dist
            z_coord = xy_dist * math.sin(x_rotate)

        else:
            # check for if we are going relatively down or up
            if x_rotate > math.radians(180):
                z_coord = -4
            else:
                z_coord = 4

            # scale x and y coords accordingly
            new_xy_dist = 4 / math.tan(x_rotate)
            x_coord *= new_xy_dist / xy_dist
            y_coord *= new_xy_dist / xy_dist

        return (x_coord, y_coord, z_coord)

    def find_motor_scalars(self, x_coord, y_coord, z_coord) -> (float, float, float):
        z_scalar = z_coord
        a_scalar = x_coord / (2 * math.cos(math.pi / 3)) + y_coord / (
            2 * math.sin(math.pi / 3)
        )
        b_scalar = x_coord / (2 * math.cos(math.pi / 3)) - y_coord / (
            2 * math.sin(math.pi / 3)
        )
        return (a_scalar, -b_scalar, z_scalar)

    # moves the ROV according to a vector specified in spherical form (r, θ, ϕ)
    def drive_vector(self, translation_vector: tuple, rotation_vector: tuple):
        r, theta, phi = cartesian_to_spherical(translation_vector)
        if r > 1:
            r = 1
        elif r < -1:
            r = -1

        yaw, roll, pitch = rotation_vector
        max_speed_coords = self.find_max_speed(phi, theta)
        a, b, z = self.find_motor_scalars(
            max_speed_coords[0] * r / 2,
            max_speed_coords[1] * r / 2,
            max_speed_coords[2] * r / 4,
        )
        self.motor_velocities = [b, a, -a, -b, z, z, z, z]

        self.calc_yaw_velocity(yaw)
        self.calc_roll_velocity(roll)
        self.calc_pitch_velocity(pitch)

        # make sure the motors don't exceed the speed limit
        for motor_num in range(len(self.motor_velocities)):
            if self.motor_velocities[motor_num] > self.speed_limit:
                self.motor_velocities[motor_num] = self.speed_limit
            elif self.motor_velocities[motor_num] < -self.speed_limit:
                self.motor_velocities[motor_num] = -self.speed_limit


        for motor_num, velocity in enumerate(self.motor_velocities):
            self.drive_motor(motor_num, velocity)


def main():
    motors = Motors()
    motors.drive_motor(0, 1)
    #  motors.test_motors()
    #  motors.drive_motor(7, 0.15)
    time.sleep(3)
    motors.stop_all()
    #  motors.drive_motors(z_velocity=0.5)
    #  time.sleep(2)
    #  motors.drive_motors()


if __name__ == "__main__":
    main()
