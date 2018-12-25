import json
from hashlib import sha256

from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import *

# Create your views here.
api_base_msgs = {
    200: "Success",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    500: ""
}


def str_to_sha256(string):
    return sha256(string.encode("UTF-8")).hexdigest()


def auth_required(func):
    def wrapper(*args, **kwargs):
        if 'login' in args[1].session:
            if args[1].session['login']:
                return func(*args, **kwargs)
            else:
                return Response(APIResponse(403).json())
        else:
            return Response(APIResponse(403).json())

    return wrapper


class APIResponse():
    def __init__(self, status_code, msg=''):
        if not msg:
            msg = api_base_msgs[status_code]
        self.status = status_code
        self.msg = msg
        self.data = {}

    def json(self):
        return json.dumps({
            "status": self.status,
            "msg": self.msg,
            "data": self.data
        })


class AcConfigList(APIView):
    @auth_required
    def get(self, request, format=None):
        exist_configs = AcConfig.objects.all()
        if exist_configs:
            serializer = AcConfigSerializer(exist_configs, many=True)
            response = APIResponse(200)
            response.data = serializer.data
            return Response(response.json())
        else:
            return Response(APIResponse(404))


class Auth(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        exist_user = self.get_object(pk=1)
        if serializer.is_valid() and (
                sha256(serializer.data["password"].encode("UTF-8")).hexdigest() == exist_user.password):
            request.session['login'] = True
            return Response(APIResponse(200).json())
        else:
            return Response(APIResponse(403).json())


class Logout(APIView):
    @auth_required
    def get(self, request, format=None):
        request.session['login'] = False
        return Response(APIResponse(200).json())


class ChangePassword(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    @auth_required
    def post(self, request, format=None):
        exist_user = self.get_object(pk=1)
        hash_original = sha256(request.data["original_password"].encode("UTF-8")).hexdigest()
        hash_new = sha256(request.data["password"].encode("UTF-8")).hexdigest()
        if hash_original == exist_user.password:
            exist_user.password = hash_new
            exist_user.save()
            request.session['login'] = False
            return Response(APIResponse(200).json())
        else:
            return Response(APIResponse(400).json())


class SetPassword(APIView):
    def get_object(self):
        try:
            return User.objects.get(pk=1)
        except User.DoesNotExist:
            raise PermissionError()

    def post(self, request, format=None):
        new_password = UserSerializer(data=request.data)
        try:
            self.get_object()
        except PermissionError:
            new_password.initial_data["password"] = str_to_sha256(new_password.initial_data["password"])
            if new_password.is_valid():
                new_password.save()
                return Response(APIResponse(200).json())
            else:
                return Response(APIResponse(403).json())
        else:
            return Response(APIResponse(400).json())


class GetPreference(APIView):
    @auth_required
    def get(self, request, format=None):
        try:
            res = APIResponse(200)
            res.data = PreferenceSerializer(Preference.objects.all(), many=True).data
            if res.data:
                return Response(res.json())
            else:
                raise Preference.DoesNotExist()
        except Preference.DoesNotExist:
            return Response(APIResponse(404).json())


class SetPreference(APIView):
    @auth_required
    def post(self, request, format=None):
        try:
            exist_preference = Preference.objects.all()
        except Preference.DoesNotExist:
            pass
        else:
            exist_preference.delete()
        new_preference = PreferenceSerializer(data=request.data)
        if new_preference.is_valid():
            new_preference.save()
            return Response(APIResponse(200).json())
        else:
            return Response(APIResponse(400).json())


class UpdateAcConfig(APIView):
    def get_object(self, pk):
        try:
            return AcConfig.objects.get(pk=pk)
        except AcConfig.DoesNotExist:
            raise Http404

    @auth_required
    def post(self, request, format=None):
        try:
            exist_config = self.get_object(pk=request.data["id"])
        except Http404:
            return Response(APIResponse(404).json())
        serializer = AcConfigSerializer(exist_config)
        new_config = AcConfigSerializer(data=request.data["config"])
        if new_config.is_valid():
            serializer.update(exist_config, new_config.data)
            return Response(APIResponse(200).json())
        else:
            return Response(APIResponse(400).json())


class GetCurrentAcConfig(APIView):
    @auth_required
    def get(self, request, format=None):
        res = APIResponse(200)
        res.data = CurrentAcConfigSerializer(CurrentAcConfig.objects.all(), many=True).data
        return Response(res.json())


class GetSleepTimes(APIView):
    @auth_required
    def get(self, request, format=None):
        res = APIResponse(200)
        res.data = SleepSerializer(Sleep.objects.all(), many=True).data
        if res.data:
            return Response(res.json())
        else:
            return Response(APIResponse(404).json())


class AddSleepTime(APIView):
    @auth_required
    def post(self, request, format=None):
        new_sleep_time = SleepSerializer(data=request.data)
        if new_sleep_time.is_valid():
            new_sleep_time.save()
            return Response(APIResponse(200).json())
        else:
            return Response(APIResponse(400).json())


class DeleteSleepTime(APIView):
    @auth_required
    def post(self, request, format=None):
        sleep_time_id = request.data["id"]
        try:
            sleep_time = Sleep.objects.get(pk=sleep_time_id)
        except Sleep.DoesNotExist:
            return Response(APIResponse(404).json())
        else:
            sleep_time.delete()
            return Response(APIResponse(200).json())


class GetBootTimes(APIView):
    @auth_required
    def get(self, request, format=None):
        res = APIResponse(200)
        res.data = BootTimeSerializer(BootTime.objects.all(), many=True).data
        if res.data:
            return Response(res.json())
        else:
            return Response(APIResponse(404).json())


class AddBootTime(APIView):
    @auth_required
    def post(self, request, format=None):
        new_boot_time = BootTimeSerializer(data=request.data)
        if new_boot_time.is_valid():
            new_boot_time.save()
            return Response(APIResponse(200).json())
        else:
            return Response(APIResponse(400).json())


class DeleteBootTime(APIView):
    @auth_required
    def post(self, request, format=None):
        boot_time_id = request.data["id"]
        try:
            boot_time = BootTime.objects.get(pk=boot_time_id)
        except BootTime.DoesNotExist:
            return Response(APIResponse(404).json())
        else:
            boot_time.delete()
            return Response(APIResponse(200).json())
