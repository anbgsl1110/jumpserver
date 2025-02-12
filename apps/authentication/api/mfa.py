# -*- coding: utf-8 -*-
#
import time

from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.serializers import ValidationError
from rest_framework.response import Response

from common.permissions import IsValidUser, NeedMFAVerify
from common.utils import get_logger
from common.exceptions import UnexpectError
from users.models.user import User
from ..serializers import OtpVerifySerializer
from .. import serializers
from .. import errors
from ..mfa.otp import MFAOtp
from ..mixins import AuthMixin


logger = get_logger(__name__)

__all__ = [
    'MFAChallengeVerifyApi', 'UserOtpVerifyApi',
    'MFASendCodeApi'
]


# MFASelectAPi 原来的名字
class MFASendCodeApi(AuthMixin, CreateAPIView):
    """
    选择 MFA 后对应操作 api，koko 目前在用
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.MFASelectTypeSerializer
    username = ''
    ip = ''

    def get_user_from_db(self, username):
        try:
            user = get_object_or_404(User, username=username)
            return user
        except Exception as e:
            self.incr_mfa_failed_time(username, self.ip)
            raise e

    def perform_create(self, serializer):
        username = serializer.validated_data.get('username', '')
        mfa_type = serializer.validated_data['type']

        self.ip = self.get_request_ip()
        self.check_mfa_is_block(username, self.ip)
        if not username:
            user = self.get_user_from_session()
        else:
            user = self.get_user_from_db(username)

        mfa_backend = user.get_active_mfa_backend_by_type(mfa_type)
        if not mfa_backend or not mfa_backend.challenge_required:
            error = _('Current user not support mfa type: {}').format(mfa_type)
            raise ValidationError({'error': error})
        try:
            mfa_backend.send_challenge()
        except Exception as e:
            raise UnexpectError(str(e))


class MFAChallengeVerifyApi(AuthMixin, CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.MFAChallengeSerializer

    def perform_create(self, serializer):
        user = self.get_user_from_session()
        code = serializer.validated_data.get('code')
        mfa_type = serializer.validated_data.get('type', '')
        self._do_check_user_mfa(code, mfa_type, user)

    def create(self, request, *args, **kwargs):
        try:
            super().create(request, *args, **kwargs)
            return Response({'msg': 'ok'})
        except errors.AuthFailedError as e:
            data = {"error": e.error, "msg": e.msg}
            raise ValidationError(data)
        except errors.NeedMoreInfoError as e:
            return Response(e.as_data(), status=200)


class UserOtpVerifyApi(CreateAPIView):
    permission_classes = (IsValidUser,)
    serializer_class = OtpVerifySerializer

    def get(self, request, *args, **kwargs):
        return Response({'code': 'valid', 'msg': 'verified'})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        otp = MFAOtp(request.user)

        ok, error = otp.check_code(code)
        if ok:
            request.session["MFA_VERIFY_TIME"] = int(time.time())
            return Response({"ok": "1"})
        else:
            return Response({"error": _("Code is invalid, {}").format(error)}, status=400)

    def get_permissions(self):
        if self.request.method.lower() == 'get' \
                and settings.SECURITY_VIEW_AUTH_NEED_MFA:
            self.permission_classes = [NeedMFAVerify]
        return super().get_permissions()
