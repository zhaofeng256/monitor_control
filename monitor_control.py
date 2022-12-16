import argparse
import ctypes
import sys

import numpy

PRIMARY_MONITOR_ID = 0
SECONDARY_MONITOR_ID = 1


class DisplayDevice(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_long),
        ("DeviceName", ctypes.c_char * 32),
        ("DeviceString", ctypes.c_char * 128),
        ("StateFlags", ctypes.c_long),
        ("DeviceID", ctypes.c_char * 128),
        ("DeviceKey", ctypes.c_char * 128),
    ]


def print_ramp(ramp_buf):
    """
    Displays the GammaArray of 256 values of R,G,B individually
    :param ramp_buf: GammaArray
    :return: None
    """
    ramp_array = numpy.frombuffer(ramp_buf, dtype=numpy.ushort)
    ramp_array = ramp_array.reshape(3, 256)
    print("red:", ramp_array[0])
    print("green:", ramp_array[1])
    print("blue:", ramp_array[2])


def set_ramp_buf(ramp_buf, gamma):
    """
    Modifies the Gamma Values array according to specified 'gamma' value
    To reset the gamma values to default, call this method with 'gamma' as 128
    :param ramp_buf: GammaArray
    :param gamma: Value of gamma between 0-255
    :return: Modified GammaValue Array
    """
    for i in range(256):
        j = i * (gamma + 128)
        if j > 65535:
            j = 65535
        ramp_buf[0][i] = ramp_buf[1][i] = ramp_buf[2][i] = j
    return ramp_buf


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--read_gamma",
        type=int,
        dest="id",
        nargs=1,
        default=[-1],
        action="store",
        help="read gamma value, need ID (enum 0, 1, 2)",
    )

    parser.add_argument(
        "-s",
        "--set_gamma",
        type=int,
        dest="value",
        nargs=2,
        default=[-1, -1],
        action="store",
        help="set gamma value, need ID (enum 0, 1, 2) and VALUE (range 0 - 255)",
    )

    args = parser.parse_args()
    if (
        args.id[0] < 0
        and args.value[0] < 0
        or (args.value[0] >= 0 and (args.value[1] < 0 or args.value[1] > 255))
    ):
        parser.print_help()

    return args.id, args.value


# noinspection PyPep8Namin


def get_display_gamma(i):

    if i < 0:
        return -1
    gamma = -1
    dd = DisplayDevice()
    dd.cb = ctypes.sizeof(dd)
    if EnumDisplayDevicesA(None, i, ctypes.byref(dd), 0):
        name = ctypes.c_char_p(dd.DeviceName)
        hdc = CreateDCA(None, name, None, None)
        if hdc:
            ramp = ((ctypes.c_ushort * 256) * 3)()
            if GetDeviceGammaRamp(hdc, ctypes.byref(ramp)):
                gamma = int(ramp[0][1]) - 128
            ReleaseDC(name, hdc)

    return gamma


def set_display_gamma(i, gamma):
    if i < 0 or gamma < 0 or gamma > 255:
        return

    dd = DisplayDevice()
    dd.cb = ctypes.sizeof(dd)
    if EnumDisplayDevicesA(None, i, ctypes.byref(dd), 0):
        name = ctypes.c_char_p(dd.DeviceName)
        hdc = CreateDCA(None, name, None, None)
        if hdc:
            ramp = ((ctypes.c_ushort * 256) * 3)()
            if GetDeviceGammaRamp(hdc, ctypes.byref(ramp)):
                set_ramp_buf(ramp, gamma)
                SetDeviceGammaRamp(hdc, ramp)
        ReleaseDC(name, hdc)


def main():
    r, w = parse_args()
    if r[0] >= 0:
        gamma = get_display_gamma(r[0])
        print(gamma)

    if w[0] >= 0:
        set_display_gamma(w[0], w[1])


if __name__ == "__main__":
    EnumDisplayDevicesA = ctypes.windll.user32.EnumDisplayDevicesA
    CreateDCA = ctypes.windll.gdi32.CreateDCA
    GetDeviceGammaRamp = ctypes.windll.gdi32.GetDeviceGammaRamp
    SetDeviceGammaRamp = ctypes.windll.gdi32.SetDeviceGammaRamp
    ReleaseDC = ctypes.windll.user32.ReleaseDC
    main()
