import time
from time import sleep
from PyQt5.QtCore import *
from Common import Common


class FpsThread(QThread, Common):

    trigger = pyqtSignal(float, bool)

    def __init__(self, excel, sheet, workbook, interval, durtime, package, lock):
        super(QThread, self).__init__()
        self.excel = excel
        self.interval = interval
        self.durtime = durtime
        self.package = package
        self.sheet = sheet
        self.workbook = workbook
        self.btn_enable = False
        self.ratio = 1
        self.lock = lock

    def run(self):

        row = 1
        last_fps = 0

        durtime = self.durtime.replace("min", "")
        interval = self.interval.replace("s", "")
        durtime = int(durtime)*60
        interval = int(interval)
        n = int(durtime / interval) + 1


        for i in range(n):
            sleep_interval = 0.001
            start_time = time.time()
            if self.check_adb(self.package) == 1:
                # cmd_fps = "adb shell service call SurfaceFlinger 1013"
                cmd_fps = "adb shell \"dumpsys SurfaceFlinger | grep flips\""
                res = self.execshell(cmd_fps)
                if res.poll() is None:
                    line = res.stdout.readline().decode('utf-8', 'ignore')
                    if line != "":
                        # fps = self.format_by_re('Result: Parcel\((\w+)', line)
                        fps = self.format_by_re('flips=(\d+)', line)
                        if len(fps) > 0:
                            fps = fps.pop()
                            fps = int(fps)
                            if last_fps == 0:
                                # fps = fps * self.ratio
                                last_fps = fps
                            else:
                                fps = fps * self.ratio
                                new_fps = fps - last_fps
                                new_fps = new_fps/interval
                                new_fps = round(new_fps, 1)

                                self.lock['fps'].acquire()
                                self.trigger.emit(new_fps, self.btn_enable)
                                last_fps = fps
                                row += 1
                                self.sheet.write(row, 3, new_fps)
                                print("fps %d" % row)
                                self.lock['battery'].release()

                while (time.time()-start_time)*1000000 <= interval * 1000000:
                    sleep_interval += 0.0000001
                    sleep(sleep_interval)
                end_time = time.time()
                avg = (end_time-start_time)*1000
                # print("Fps为%f" % avg)

        self.btn_enable = True
        self.trigger.emit(0, self.btn_enable)
        # self.workbook.save(self.excel)

