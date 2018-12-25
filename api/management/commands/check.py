import datetime
import getpass

import RPi.GPIO as GPIO
from django.core.management.base import BaseCommand
from pytz import timezone

from api.serializers import *
from ._encode_IR import *


class Command(BaseCommand):
    def send_signal(self, power=False, wm=0, tp=0, ws=0, fl=False, sm=False, hu=False, li=False, an=False, de=False,
                    ve=False, udf=False, lrf=False, td=0, es=False):
        signal = State(power, wm, tp, ws, fl, sm, hu, li, an, de, ve, udf, lrf, td, es)
        write_control_file(encode_signal(gen_code(signal)))
        send_IR_signal()

    def load_config(self):
        preference = PreferenceSerializer(Preference.objects.all(), many=True).data[0]
        self.delay = preference["delay"]
        self.prepare = preference["prepare"]
        self.season = preference["season"]
        self.sleep_times = SleepSerializer(Sleep.objects.all(), many=True).data
        self.boot_times = BootTimeSerializer(BootTime.objects.all(), many=True).data
        self.ac_configs = AcConfigSerializer(AcConfig.objects.all(), many=True).data
        self.current_time = datetime.datetime.now(tz=timezone('Asia/Shanghai')) \
            .isoformat(timespec='minutes').split('T')[1].split('+')[0]
        try:
            self.no_people_time_tuple = [i for i in NoPeopleTime.objects.all()[0].minute.split(':')]
        except IndexError:
            self.no_people_time_tuple = [i for i in self.current_time.split(":")]
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.IN)
        self.people_state = False

    def is_in_sleep_time(self):
        for sleep_time in self.sleep_times:
            start_sleep_time_hour, start_sleep_time_minute = sleep_time["start"].split(":")
            end_sleep_time_hour, end_sleep_time_minute = sleep_time["end"].split(":")
            current_time_hour, current_time_minute, current_time_sec = self.current_time.split(":")
            if start_sleep_time_hour > end_sleep_time_hour:
                if current_time_hour > start_sleep_time_hour or current_time_hour < end_sleep_time_hour:
                    return True
                elif current_time_hour == start_sleep_time_hour:
                    if current_time_minute >= start_sleep_time_minute:
                        return True
                    else:
                        return False
                elif current_time_hour == end_sleep_time_hour:
                    if current_time_minute <= start_sleep_time_minute:
                        return True
                    else:
                        return False
            else:
                if current_time_hour > start_sleep_time_hour and current_time_hour < end_sleep_time_hour:
                    return True
                elif current_time_hour == start_sleep_time_hour:
                    if current_time_minute >= start_sleep_time_minute:
                        return True
                    else:
                        return False
                elif current_time_hour == end_sleep_time_hour:
                    if current_time_minute <= start_sleep_time_minute:
                        return True
                    else:
                        return False
        return False

    def handle(self, *args, **options):
        if getpass.getuser() != 'root':
            print('Please run as root!')
            exit(-1)
        while True:
            self.load_config()
            current_time_hour, current_time_minute = self.current_time.split(":")
            current_log_time = datetime.datetime.now(tz=timezone('Asia/Shanghai')).isoformat(timespec='minutes')
            log_file = open('check.log', 'a')
            if self.people_state:
                try:
                    exist_no_people_time = NoPeopleTime.objects.all()[0]
                except IndexError:
                    exist_no_people_time = NoPeopleTime(minute="{0}:{1}".format(current_time_hour, current_time_minute))
                exist_no_people_time.minute = "{0}:{1}".format(current_time_hour, current_time_minute)
                exist_no_people_time.save()
                print('{0} NoPeopleTime Updated.'.format(current_log_time))
                log_file.write('{0} NoPeopleTime Updated.\n'.format(current_log_time))

            if not self.is_in_sleep_time():
                if (not self.people_state) and (current_time_hour >= self.no_people_time_tuple[0]) and (
                        int(current_time_minute) - int(self.no_people_time_tuple[1]) >= self.delay):
                    for t in range(0, 5):
                        self.send_signal()
                        log_file.write(
                            '{0} AC Closed due to no people activity keeps more than delay time.\nRepeat {1} times.'.format(
                                current_log_time, t + 1))
                        print(
                            '{0} AC Closed due to no people activity keeps more than delay time.\nRepeat {1} times.'.format(
                                current_log_time, t + 1))
                    try:
                        current_config = CurrentAcConfig.objects.all()[0]
                        current_config.delete()
                    except IndexError:
                        pass
                    new_current_config = CurrentAcConfig(power=False, working_mode=0, temperature=0, wind_speed=0)
                    new_current_config.save()

                else:
                    pass

            for boot_time in self.boot_times:
                boot_time_hour, boot_time_minute = boot_time["start"].split(":")
                if boot_time_hour == current_time_hour and int(boot_time_minute) - int(
                        current_time_minute) <= self.prepare:
                    for config in self.ac_configs:
                        if config["season"] == self.season:
                            for t in range(0, 5):
                                self.send_signal(config["power"], config["working_mode"], config["temperature"],
                                                 config["wind_speed"], config["wind_flap"], config["sleep_mode"],
                                                 config["anion"], config["light"], config["desiccation"],
                                                 config["ventilation"], config["vertical_flap"],
                                                 config["horizontal_flap"],
                                                 config["temperature_display"], config["energy_saving"])
                                log_file.write('{0} AC Opened due to reach preset BootTime.\nRepeat {1} times.'.format(
                                    current_log_time, t + 1))
                                print('{0} AC Opened due to reach preset BootTime.\nRepeat {1} times.'.format(
                                    current_log_time, t + 1))
                            try:
                                current_config = CurrentAcConfig.objects.all()[0]
                                current_config.delete()
                            except IndexError:
                                pass
                            new_current_config = CurrentAcConfig(power=config["power"],
                                                                 working_mode=config["working_mode"],
                                                                 temperature=config["temperature"],
                                                                 wind_speed=config["wind_speed"],
                                                                 wind_flap=config["wind_flap"],
                                                                 sleep_mode=config["sleep_mode"],
                                                                 anion=config["anion"], light=config["light"],
                                                                 desiccation=config["desiccation"],
                                                                 ventilation=config["ventilation"],
                                                                 vertical_flap=config["vertical_flap"],
                                                                 horizontal_flap=config["horizontal_flap"],
                                                                 temperature_display=config["temperature_display"],
                                                                 energy_saving=config["energy_saving"])
                            new_current_config.save()

            time.sleep(10)
