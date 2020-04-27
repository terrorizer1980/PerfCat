import re
import time
import copy

from PyQt5.QtCore import *

from Common import Common
from Cpu import CpuThread


class MemThread(QThread, Common):

    trigger = pyqtSignal(float, bool)

    def __init__(self, excel, sheet, workbook, interval, durtime, package):
        super(QThread, self).__init__()
        self.excel = excel
        self.interval = interval
        self.durtime = durtime
        self.package = package
        self.sheet = sheet
        self.workbook = workbook
        self.btn_enable = False

    def run(self):
        global lock
        row = 1
        avg_sum = 0

        durtime = self.durtime.replace("min", "")
        interval = self.interval.replace("s", "")
        durtime = int(durtime) * 60
        interval = int(interval)
        n = int(durtime / interval)
        name = self.get_package(self.package)

        for i in range(n):
            if self.check_adb(self.package) == 1:
                row += 1
                cmd_mem = "adb shell dumpsys meminfo " + name
                res = self.execshell(cmd_mem)
                start_time = time.time()
                sleep_interval = 0.001

                while res.poll() is None:
                    line = res.stdout.readline().decode('utf-8', 'ignore')
                    if "TOTAL" in line:
                        mem = re.findall('TOTAL\:|\s*TOTAL\s*(\d+)', line)
                        if mem:
                            mem = mem.pop()
                            if mem != '':
                                mem = int(mem)/1024
                                mem = round(mem, 2)
                                # mem = format(mem, '.2f')
                                mem = float(mem)
                                self.trigger.emit(mem, self.btn_enable)
                                self.sheet.write(row, 2, mem)

                while (time.time() - start_time) * 1000000 <= interval * 1000000:
                    sleep_interval += 0.0000001
                    time.sleep(sleep_interval)
                end_time = time.time()
                avg = (end_time - start_time) * 1000
                print("内存为%f" % avg)

        self.btn_enable = True
        self.trigger.emit(0, self.btn_enable)
        print("save")
        self.workbook.save(self.excel)


