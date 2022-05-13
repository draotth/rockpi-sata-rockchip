#!/usr/bin/env python3
import sys
import fan
import misc
try:
    import oled
    top_board = 1
except Exception:
    top_board = 0
import multiprocessing as mp
import sdnotify

q = mp.Queue()
lock = mp.Lock()

action = {
    'none': lambda: 'nothing',
    'slider': lambda: oled.slider(lock),
    'switch': lambda: misc.fan_switch(),
    'reboot': lambda: misc.check_call('reboot'),
    'poweroff': lambda: misc.check_call('poweroff'),
}


def receive_key(q):
    while True:
        func = misc.get_func(q.get())
        action[func]()


def main():
    n = sdnotify.SystemdNotifier()
    if sys.argv[-1] == 'on':
        n.notify("STATUS=Turning on disks...")
        if top_board:
            oled.welcome()
        if misc.disk_turn_on():
            n.notify("STATUS=Active: Disks enabled.")
        else:
            n.notify("STATUS=Active: Timed out waiting on disks to enable. They may come up anyway.")
        n.notify("READY=1")

        if top_board:
            p0 = mp.Process(target=receive_key, args=(q,))
            p1 = mp.Process(target=misc.watch_key, args=(q,))
            p2 = mp.Process(target=oled.auto_slider, args=(lock,))
            p3 = mp.Process(target=fan.running)

            p0.start()
            p1.start()
            p2.start()
            p3.start()
            p3.join()
        else:
            p3 = mp.Process(target=fan.running)
            p3.start()
            p3.join()


    elif sys.argv[-1] == 'off':
        n.notify("STOPPING=1")
        n.notify("STATUS=")
        if top_board:
            oled.goodbye()
        misc.disk_turn_off()
        exit(0)


if __name__ == '__main__':
    main()
