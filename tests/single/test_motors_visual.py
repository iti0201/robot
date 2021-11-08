# Enable parent directory import
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import commRaspMain
import time
import matplotlib.pyplot as plt

r = commRaspMain.PiBot()
r._motors_enable()
r._encoders_enable()

r._motorL_set(0)
r._motorR_set(0)


def motor_test(motor, encoder_index, power, test_time=1):
    r._encoders_get()
    encoder_initial = float(r.encoder[encoder_index])

    motor(power)
    time.sleep(test_time)
    motor(0)
    time.sleep(0.25)

    r._encoders_get()
    encoder_final = float(r.encoder[encoder_index])
    dps = -(encoder_final - encoder_initial) / test_time

    print("speed:", dps)
    if power != 0:
        print("efficiency:", dps / power)
        return dps / power


def test_motor(motor, encoder_index):
    results = []

    powers = []
    efficiencies = []
    for power in range(10, 101, 10):
        print("power:", power)
        powers.append(power)
        efficiencies.append(motor_test(motor, encoder_index, power, 0.5))
        print()
    results.append(("high_speed_forward", powers, efficiencies))

    powers = []
    efficiencies = []
    for power in range(-10, -101, -10):
        print("power:", power)
        powers.append(power)
        efficiencies.append(motor_test(motor, encoder_index, power, 0.5))
        print()
    results.append(("high_speed_backward", powers, efficiencies))

    powers = []
    efficiencies = []
    for power in range(2, 20, 2):
        print("power:", power)
        powers.append(power)
        efficiencies.append(motor_test(motor, encoder_index, power, 0.5))
        print()
    results.append(("low_speed_forward", powers, efficiencies))

    powers = []
    efficiencies = []
    for power in range(-2, -20, -2):
        print("power:", power)
        powers.append(power)
        efficiencies.append(motor_test(motor, encoder_index, power, 0.5))
        print()
    results.append(("low_speed_backward", powers, efficiencies))

    return results


def plot_results(title, data, xlabel="power(%)", ylabel="efficiency(deg/s/%)"):
    colors = "bgrcmyk"
    color_index = 0
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for result in data:
        ax1.plot(result[1], result[2], c=colors[color_index], label=result[0])
        color_index = (color_index + 1) % len(colors)
    plt.legend(loc='upper left')
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)
    plt.ion()
    plt.show()
    plt.draw()
    plt.pause(0.001)


if __name__ == "__main__":
    print("Testing right motor")
    right_results = test_motor(r._motorR_set, 0)
    plot_results("right motor", right_results)

    print("Testing left motor")
    left_results = test_motor(r._motorL_set, 1)
    plot_results("left motor", left_results)

    input()
