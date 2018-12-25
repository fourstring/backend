from rest_framework import serializers

from api.models import AcConfig, User, Preference, Sleep, BootTime, NoPeopleTime, CurrentAcConfig


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'password'
        )


class AcConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcConfig
        fields = (
            'id',
            'power', 'working_mode', 'temperature', 'wind_speed', 'wind_flap', 'sleep_mode', 'light', 'anion',
            'desiccation', 'ventilation', 'vertical_flap', 'horizontal_flap', 'temperature_display', 'energy_saving',
            'season'
        )


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = (
            'id',
            'prepare',
            'delay',
            'season'
        )


class CurrentAcConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentAcConfig
        fields = (
            'id',
            'power', 'working_mode', 'temperature', 'wind_speed', 'wind_flap', 'sleep_mode', 'light', 'anion',
            'desiccation', 'ventilation', 'vertical_flap', 'horizontal_flap', 'temperature_display', 'energy_saving',
            'season'
        )


class SleepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sleep
        fields = (
            'id',
            'start',
            'end'
        )


class BootTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BootTime
        fields = (
            'id',
            'start'
        )


class NoPeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoPeopleTime
        fields = (
            'id',
            'minute'
        )
