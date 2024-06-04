import wmi
import winreg
import os
import math
# import tkinter as tk
from tkinter import *
import win32api, win32con

# 获取显示器 主机配置信息
w = wmi.WMI()
global list
list = []


def info():
    # 显示器配置信息
    PATH = "SYSTEM\\ControlSet001\\Enum\\"

    # 获取屏幕信息
    monitors = w.Win32_DesktopMonitor()
    list.append("-------------------显示器配置信息--------------------")
    for m in monitors:
        subPath = m.PNPDeviceID  #
        # 可能有多个注册表
        if subPath == None:
            continue
        # 这个路径这里就是你的显示器在注册表中的路径，比如我现在的电脑是在HKEY_LOCAL_MACHINE下面的路径：
        # \SYSTEM\ControlSet001\Enum\DISPLAY\CMN1604\1&8713bca&0&UID0\Device Parameters
        infoPath = PATH + subPath + "\\Device Parameters"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, infoPath)
        # 屏幕信息按照一定的规则保存（EDID）
        value = winreg.QueryValueEx(key, "EDID")[0]
        winreg.CloseKey(key)

        # 屏幕实际尺寸
        width, height = value[21], value[22]
        # 推荐屏幕分辨率
        widthResolution = value[56] + (value[58] >> 4) * 256
        heightResolution = value[59] + (value[61] >> 4) * 256
        # 屏幕像素密度（Pixels Per Inch）
        widthDensity = widthResolution / (width / 2.54)
        heightDensity = heightResolution / (height / 2.54)

        # print("屏幕宽度：", str(width), " (厘米)")
        # print("屏幕高度：", str(height), " (厘米)")
        # print("水平分辩率: ", str(widthResolution), " (像素)")
        # print("垂直分辩率: ", str(heightResolution), " (像素)")
        # # 保留小数点固定位数的两种方法
        # print("水平像素密度: ", round(widthDensity, 2), " (PPI)")
        # print("垂直像素密度: ", "%2.f" % heightDensity, " (PPI)")

        width1 = "屏幕宽度" + str(width) + "（厘米）"
        height1 = "屏幕高度：" + str(height) + " (厘米)"
        yingcun = math.sqrt(int(width * width + height * height))

        yc = format(yingcun / 2.54, '.0f')
        yingcun1 = "屏幕尺寸:" + str(yc) + "(英寸)"
        widthResolution1 = "水平分辩率: " + str(widthResolution) + " (像素)"
        heightResolution1 = "垂直分辩率: " + str(heightResolution) + " (像素)"
        # data =[]
        list.append(width1)
        list.append(height1)
        list.append(yingcun1)
        list.append(widthResolution1)
        list.append(heightResolution1)

    list.append("------------------电脑信息--------------------")
    for BIOSs in w.Win32_ComputerSystem():
        list.append("电脑名称: %s" % BIOSs.Caption)
        list.append("使 用 者: %s" % BIOSs.UserName)
    # 获取序列号
    for zb_msg in w.Win32_BaseBoard():
        zbs = str(zb_msg.SerialNumber)
        try:
            xlh = zbs.split('/')[1]
            list.append("序列号: %s" % str(xlh))

        except IndexError as e:
            print(e)
            try:
                xlh = zbs.split('.')[1]
                list.append("序列号: %s" % str(xlh))
            except IndexError as e:
                list.append("序列号1: %s" % str(zbs))

        # zbs = str(zb_msg.SerialNumber).split('/')[1]

        # list.append("序列号: %s" % str(zb_msg.SerialNumber))
        # print(str(zb_msg.SerialNumber).split('/'))
        # list.append("序列号: %s" % zbs)

    for address in w.Win32_NetworkAdapterConfiguration(ServiceName="e1dexpress"):
        list.append("IP地址: %s" % address.IPAddress[0])
        list.append("MAC地址: %s" % address.MACAddress)
    for BIOS in w.Win32_BIOS():
        list.append("使用日期: %s" % BIOS.Description)
        list.append("主板型号: %s" % BIOS.SerialNumber)
    for processor in w.Win32_Processor():
        list.append("CPU型号: %s" % processor.Name.strip())
    for memModule in w.Win32_PhysicalMemory():
        totalMemSize = int(memModule.Capacity)
        list.append("内存厂商: %s" % memModule.Manufacturer)
        list.append("内存型号: %s" % memModule.PartNumber)
        list.append("内存大小: %.2fGB" % (totalMemSize / 1024 ** 3))

    for disk in w.Win32_DiskDrive(InterfaceType="IDE"):
        diskSize = int(disk.size)
        list.append("磁盘名称: %s" % disk.Caption)
        list.append("磁盘大小: %.2fGB" % (diskSize / 1024 ** 3))
    for xk in w.Win32_VideoController():
        list.append("显卡名称: %s" % xk.name)


def main():
    info()
    print(len(list))
    # 创建主窗口
    win = Tk()
    win.title('电脑配置')
    text = Text(win, width=60, height=30, undo=True, autoseparators=False)
    text.pack()
    for i in list:
        text.insert(INSERT, str(i) + '\n')

    win.mainloop()

    with open('diannao.txt', 'w+', encoding='utf-8') as d:
        for li in list:
            print(li)
            l = li + "\n"
            d.write(l)


main()