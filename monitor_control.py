import argparse
import ctypes
import datetime
from pathlib import Path

import numpy


class DisplayDevice(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_long),
        ("DeviceName", ctypes.c_char * 32),
        ("DeviceString", ctypes.c_char * 128),
        ("StateFlags", ctypes.c_long),
        ("DeviceID", ctypes.c_char * 128),
        ("DeviceKey", ctypes.c_char * 128),
    ]


def save_ramp_buf(i, p):
    if i < 0:
        return

    dd = DisplayDevice()
    dd.cb = ctypes.sizeof(dd)
    if EnumDisplayDevicesA(None, i, ctypes.byref(dd), 0):
        name = ctypes.c_char_p(dd.DeviceName)
        hdc = CreateDCA(None, name, None, None)
        if hdc:
            ramp = ((ctypes.c_ushort * 256) * 3)()
            if GetDeviceGammaRamp(hdc, ctypes.byref(ramp)):
                ramp_array = numpy.frombuffer(ramp, dtype=numpy.ushort)
                ramp_array = ramp_array.reshape(3, 256)
                if p:
                    print("red:\n", ramp_array[0])
                    print("green:\n", ramp_array[1])
                    print("blue:\n", ramp_array[2])
                now = datetime.datetime.now()
                file_name = now.strftime("RGB_%Y%m%d%H%M%S")
                numpy.save(file_name, ramp_array)
                print("save as:", file_name, ".npy")
            ReleaseDC(name, hdc)


def load_ramp_buf(i, file_path, p):
    dd = DisplayDevice()
    dd.cb = ctypes.sizeof(dd)
    if EnumDisplayDevicesA(None, i, ctypes.byref(dd), 0):
        name = ctypes.c_char_p(dd.DeviceName)
        hdc = CreateDCA(None, name, None, None)
        if hdc:
            try:
                ramp_array = numpy.load(str(file_path))
            except Exception as e:
                print(f"错误：{e}")
                ReleaseDC(name, hdc)
                return
            if p:
                print("red:\n", ramp_array[0])
                print("green:\n", ramp_array[1])
                print("blue:\n", ramp_array[2])
            ramp = numpy.ctypeslib.as_ctypes(ramp_array)
            SetDeviceGammaRamp(hdc, ramp)
        ReleaseDC(name, hdc)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--id",
        type=int,
        dest="id",
        default=-1,
        action="store",
        help="select display id, need ID (enum 0, 1, 2)",
    )

    parser.add_argument(
        "-s",
        "--save",
        dest="s",
        action='store_true',
        default=False,
        help="save rgb data as file",
    )

    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        dest="f",
        action='store',
        nargs=1,
        default=None,
        help="load rgb data from file",
    )

    parser.add_argument(
        "-p",
        "--print",
        dest="p",
        action='store_true',
        default=False,
        help="print rgb buffer",
    )

    args = parser.parse_args()

    if args.id < 0:
        parser.print_help()

    return args.id, args.s, args.f, args.p


def main():
    i, s, f, p = parse_args()

    if s and i >= 0:
        save_ramp_buf(i, p)

    if f is not None and i >= 0:
        if f[0].exists():
            load_ramp_buf(i, f[0], p)
        else:
            print("file not exists")


if __name__ == "__main__":
    EnumDisplayDevicesA = ctypes.windll.user32.EnumDisplayDevicesA
    CreateDCA = ctypes.windll.gdi32.CreateDCA
    GetDeviceGammaRamp = ctypes.windll.gdi32.GetDeviceGammaRamp
    SetDeviceGammaRamp = ctypes.windll.gdi32.SetDeviceGammaRamp
    ReleaseDC = ctypes.windll.user32.ReleaseDC
    main()
