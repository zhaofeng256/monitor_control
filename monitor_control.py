import ctypes
import numpy
import sys

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
        iValue = i * (gamma + 128)
        if iValue > 65535:
            iValue = 65535
        ramp_buf[0][i] = ramp_buf[1][i] = ramp_buf[2][i] = iValue
    return ramp_buf


if __name__ == "__main__":

    EnumDisplayDevicesA = ctypes.windll.user32.EnumDisplayDevicesA
    CreateDCA = ctypes.windll.gdi32.CreateDCA
    GetDeviceGammaRamp = ctypes.windll.gdi32.GetDeviceGammaRamp
    SetDeviceGammaRamp = ctypes.windll.gdi32.SetDeviceGammaRamp
    ReleaseDC = ctypes.windll.user32.ReleaseDC

    dev = DisplayDevice()
    dev.cb = ctypes.sizeof(dev)
    if not EnumDisplayDevicesA(None, PRIMARY_MONITOR_ID, ctypes.byref(dev), 0):
        print("failed to enum display list")
        sys.exit(1)

    # print(dev.DeviceName)

    hwnd = ctypes.c_char_p(dev.DeviceName)
    hdc = CreateDCA(None, hwnd, None, None)

    if not hdc:
        print("HDC not found")
    else:
        ramp_buf = ((ctypes.c_ushort * 256) * 3)()
        if GetDeviceGammaRamp(hdc, ctypes.byref(ramp_buf)):
            # print_ramp(ramp_buf)
            gamma = int(ramp_buf[0][1]) - 128
            if len(sys.argv) != 2:
                print("Please set gamma value [0 - 255] ({:d}):".format(gamma), end=" ")
                try:
                    v = int(input())
                except:
                    v = -1
            else:
                v = int(sys.argv[1]) # can be aby value in 0-255 (as per my system)

            if (v >= 0 and v<=255):
                gamma = v
                set_ramp_buf(ramp_buf, gamma)
                SetDeviceGammaRamp(hdc, ctypes.byref(ramp_buf))
                ReleaseDC(hwnd, hdc)
            else:
                print("invalid value")
