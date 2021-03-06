#!/usr/bin/python3
import time
import misc
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

font = {
    '10': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 10),
    '11': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 11),
    '12': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 12),
    '14': ImageFont.truetype('fonts/DejaVuSansMono-Bold.ttf', 14),
}

#pin13(bcm23)
misc.set_mode(13, 0)
time.sleep(0.2)
misc.set_mode(13, 1)

def disp_init():
    if 'disp' in globals():
        return disp
    newDisp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=7)
    [getattr(newDisp, x)() for x in ('begin', 'clear', 'display')]
    return newDisp


try:
    disp = disp_init()
except Exception:
    misc.open_pwm_i2c()
    time.sleep(0.2)
    try:
        disp = disp_init()
    except Exception as ex:
        print('Failed to start oled display')
        print(ex)

image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)


def disp_show():
    if not 'disp' in globals():
        print('Disp not initialized, cannot show')
        return
    try:
        im = image.rotate(180) if misc.conf['oled']['rotate'] else image
        disp.image(im)
        disp.display()
        draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    except Exception as ex:
        print('Failed to disp_show')
        print(ex)

def welcome():
    draw.text((0, 0), 'ROCK Pi SATA HAT', font=font['14'], fill=255)
    draw.text((32, 16), 'loading...', font=font['12'], fill=255)
    disp_show()


def goodbye():
    draw.text((32, 8), 'Good Bye ~', font=font['14'], fill=255)
    disp_show()
    time.sleep(2)
    disp_show()  # clear


def put_disk_info():
    k, v = misc.get_disk_info()
    text1 = 'Disk: {} {}'.format(k[0], v[0])

    if len(k) == 5:
        text2 = '{} {}  {} {}'.format(k[1], v[1], k[2], v[2])
        text3 = '{} {}  {} {}'.format(k[3], v[3], k[4], v[4])
        page = [
            {'xy': (0, -2), 'text': text1, 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': text2, 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': text3, 'fill': 255, 'font': font['11']},
        ]
    elif len(k) == 3:
        text2 = '{} {}  {} {}'.format(k[1], v[1], k[2], v[2])
        page = [
            {'xy': (0, 2), 'text': text1, 'fill': 255, 'font': font['12']},
            {'xy': (0, 18), 'text': text2, 'fill': 255, 'font': font['12']},
        ]
    else:
        page = [{'xy': (0, 2), 'text': text1, 'fill': 255, 'font': font['14']}]

    return page


def gen_pages():
    pages = {
        0: [
            {'xy': (0, -2), 'text': misc.get_info('up'), 'fill': 255, 'font': font['11']},
            {'xy': (0, 10), 'text': misc.get_cpu_temp(), 'fill': 255, 'font': font['11']},
            {'xy': (0, 21), 'text': misc.get_info('ip'), 'fill': 255, 'font': font['11']},
        ],
        1: [
            {'xy': (0, 2), 'text': misc.get_info('cpu'), 'fill': 255, 'font': font['12']},
            {'xy': (0, 18), 'text': misc.get_info('men'), 'fill': 255, 'font': font['12']},
        ],
        2: put_disk_info()
    }

    return pages


def slider(lock):
    with lock:
        try:
            for item in misc.slider_next(gen_pages()):
                draw.text(**item)
        except Exception as ex:
            print('Draw text failed')
            print(ex)
        disp_show()


def auto_slider(lock):
    while misc.conf['slider']['auto']:
        slider(lock)
        misc.slider_sleep()
    else:
        slider(lock)
