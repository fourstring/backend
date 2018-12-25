#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import time

valid_num = [600, 1600, 4500, 9000, 20000]
field_len = [1, 3, 1, 2, 1, 1, 4, 8, 5, 10, 1, 1, 3, 1, 3, 2, 16, 1, 1, 4]


class State:
    def __init__(self, power=False, wm=0, tp=0, ws=0, fl=False, sm=False, hu=False, li=False, an=False, de=False,
                 ve=False, udf=False, lrf=False, td=0, es=False):
        self.power_on = power
        self.working_mode = wm  # 0自动 1制冷 2加湿 3送风 4制热
        self.temperature = tp  # 0->16℃ 15->30℃
        self.wind_speed = ws  # 0自动 1一级 2二级 3三级
        self.flap_on = fl
        self.sleep_mode = sm
        self.humidification = hu
        self.light = li
        self.anion = an
        self.desiccation = de
        self.ventilation = ve
        self.up_down_flap = udf
        self.left_right_flap = lrf
        self.temperature_display = td  # 0不清楚 1室内 2室外
        self.energy_saving = es


def most_close_to(num):
    dis = [i - num for i in valid_num]
    return valid_num[dis.index(min(dis, key=abs))]


def decode_byte(_pulse, _space):
    # print('decode %d %d' % (_pulse, _space))
    command = (most_close_to(_pulse), most_close_to(_space))
    if command == (600, 600):
        return '0'
    elif command == (600, 1600):
        return '1'
    elif command == (9000, 4500):
        return 'S'
    elif command == (600, 20000):
        return 'C'


def encode_byte(_code):
    signal = []
    for c in _code:
        if c == 'S':
            signal.extend([9000, 4500])
        elif c == 'C':
            signal.extend([600, 20000])
        elif c == '0':
            signal.extend([600, 600])
        elif c == '1':
            signal.extend([600, 1600])
    return signal


def calc_int(_num, _len=1):
    s = ''
    _num = int(_num)
    for i in range(_len):
        if _num % 2 == 0:
            s += '0'
        else:
            s += '1'
        _num //= 2
    return s


def gen_code(_state: State):
    code = 'S'
    code += calc_int(_state.working_mode, 3)
    code += calc_int(_state.power_on)
    code += calc_int(_state.wind_speed, 2)
    code += calc_int(_state.flap_on)
    code += calc_int(_state.sleep_mode)
    code += calc_int(_state.temperature, 4)
    code += '0' * 8  # 定时暂不可用
    code += calc_int(_state.humidification)
    code += calc_int(_state.light)  # 灯光
    code += calc_int(_state.anion)  # 健康
    code += calc_int(_state.desiccation)  # 干燥 辅热
    code += calc_int(_state.ventilation)  # 换气
    code += '0001010010C'
    code += calc_int(_state.up_down_flap)
    code += '0' * 3
    code += calc_int(_state.left_right_flap)
    code += '0' * 3
    code += calc_int(_state.temperature_display, 2)
    code += '0001000000000000'
    code += calc_int(_state.energy_saving)  # 节能
    code += '0'

    check_code = _state.working_mode + _state.temperature + _state.left_right_flap + _state.ventilation + 4
    check_code %= 16
    check_code = calc_int(check_code, 4)
    if not _state.power_on:
        check_code = list(check_code)
        if check_code[-1] == '0':
            check_code[-1] = '1'
        else:
            check_code[-1] = '0'
        check_code = ''.join(check_code)
    code += check_code

    return code


def encode_signal(_code):
    _signal = []
    for ch in _code:
        _signal.extend(encode_byte(ch))
    _signal.append(600)
    return _signal


def write_control_file(_signal):
    # f = open('air_control.lircd.conf', 'w')
    f = open('/etc/lirc/lircd.conf.d/aircon.lircd.conf', 'w')
    f.write('begin remote\n\n')
    f.write('  name  aircon\n')
    f.write('  flags RAW_CODES\n')
    f.write('  eps            30\n')
    f.write('  aeps          100\n\n')
    f.write('  gap          19991\n\n')
    f.write('      begin raw_codes\n\n')
    f.write('          name on\n\n')
    # for item in _signal:
    #     f.write(str(item) + ' ')
    cur = 0
    for item in _signal:
        cur += 1
        f.write('% 9d' % item)
        if cur % 6 == 0:
            f.write('\n')
        if item == 20000:
            f.write('\n\n')
            cur = 0
    f.write('\n      end raw_codes\n\n')
    f.write('end remote\n')
    f.close()


def print_code(_code):
    cur = 0
    for item_len in field_len:
        print(_code[cur:cur + item_len], end=' ')
        cur += item_len
    print()


def send_IR_signal():
    os.system('service lircd restart')
    time.sleep(1)
    os.system('irsend SEND_ONCE aircon on')


if __name__ == '__main__':
    '''f = open('signal.txt')
    code = str('')
    for line in f:
        item_pulse = line.split(' ')
        if item_pulse[0] not in ['pulse', 'space']:
            continue
        elif item_pulse[0] == 'pulse':
            pulse = int(item_pulse[1])
        elif item_pulse[0] == 'space':
            space = int(item_pulse[1])
            if space > 100000:
                print_code(code)
                code = str('')
                continue
            code += decode_byte(pulse, space)
    print_code(code)'''

    state_close = State()
    state_open = State(True, 4, 24, 1, td=True)
    write_control_file(encode_signal(gen_code(state_close)))
    for i in range(1, 6):
        send_IR_signal()
        print('Sent.close')
        time.sleep(1)
    time.sleep(300)
    write_control_file(encode_signal(gen_code(state_open)))
    for i in range(1, 6):
        send_IR_signal()
        print('Sent.open')
        time.sleep(1)

    # while True:
    #     send_IR_signal()
    #     print('Sent.')
    #     time.sleep(1)

# 校验码可能为r(r(模式)+r(温度)+左右扫风+换气+100)
