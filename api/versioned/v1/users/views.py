from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from api.versioned.v1.users.serializers import UserSerializer, UserCreateSerializer, UserLoginSerializer, \
    UserUpdateSerializer, ProfileSerializer, RefreshTokenSerializer
from common.permissions import IsOwnerOrAdminUser, IsOwner
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.signals import user_logged_in
from common.viewsets import MappingViewSetMixin
from rest_framework.serializers import Serializer
from api.bases.users.models import Profile, Image, User, ExpiringToken
from axes.utils import reset as axes_reset

class UserViewSet(MappingViewSetMixin, viewsets.ModelViewSet):
    """
    create:[유저 생성]
    유저를 생성한다.

    retrieve:[유저 상세 조회 - 토큰 사용]
    유저의 상세 정보를 조회합니다.

    partial_update:[유저 정보 업데이트 - 토큰 사용]
    유저 정보를 업데이트 합니다.

    destroy:[유저 삭제]
    유저를 삭제합니다. 삭제시 해당 유저에 관련된 모든 데이터가 삭제 됩니다.

    health_check:[유저 토큰 상태 체크]
    현재 유저의 토큰 상태를 확인하고, 토큰의 만료시간을 연장합니다.

    logout:[유저 로그아웃]
    유저를 로그아웃 처리합니다.
    """
    queryset = get_user_model().objects.all().prefetch_related('groups', 'user_permissions')
    serializer_class = UserSerializer
    serializer_action_map = {
        'create': UserCreateSerializer,
        'partial_update': UserUpdateSerializer,
        'logout': Serializer,
        'health_check': Serializer,
    }

    permission_classes = [IsOwner]
    permission_classes_map = {
        'create': [AllowAny],
        'destroy': [IsOwnerOrAdminUser],
        'logout': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'health_check': [IsAuthenticated],
    }

    def get_queryset(self):
        return self.queryset.filter(email=self.request.user)

    def get_object(self):
        return self.get_queryset().get()

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.permission_classes_map.get(self.action, None):
            permission_classes = self.permission_classes_map[self.action]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.serializer_action_map.get(self.action, None):
            return self.serializer_action_map[self.action]
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save()
        axes_reset(username=serializer.data.get('email'))

    @method_decorator(never_cache)
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response(status=HTTP_200_OK)

    def health_check(self, request):
        return Response(status=HTTP_200_OK)

class UserLoginTokenViewSet(viewsets.GenericViewSet):

    """
    create:[로그인]
    일정 횟수(**기본:5회**)만큼 연속 로그인 실패시 계정이 잠깁니다.<br>
    잠긴 계정은 일정 시간(**기본:30분**) 기준으로 잠김 해제됩니다.<br>
    토큰의 만료 시점은 서버에서 관리되며, 토큰 만료시 권한이 필요한 API를 호출하는 경우 status 403이 전달됩니다.<br>
    중복 로그인 허용됩니다.<br>
    force_login 사용시 기존 발급 토큰은 삭제됩니다. (중복 로그인 방지 효과)<br>

    **로그인 실패시(401)에 대한 코드 정의**
    * authentication_failed : 아이디/비밀번호 오류
    * not_authenticated : 비활성화 유저
    """
    permission_classes = [AllowAny, ]
    serializer_class = UserLoginSerializer

    @method_decorator(never_cache)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.data.get('user')
            axes_reset(username=request.data.get('email'))

            data = serializer.data
            site = get_current_site(request)

            _user = get_user_model().objects.get(is_active=True, email=user.get('email'), site=site)

            user_logged_in.send(sender=_user.__class__, request=request, user=_user)

            return Response(data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class UserProfileOnwerViewSet(MappingViewSetMixin, viewsets.ModelViewSet):
    """
    retrieve:[유저 프로파일 조회]

    ** 이동통신사(mobile_carrier) 코드 정의 **

    | **mobile_carrier** | **정의**
    |:------:|:----------
    |01| SKT
    |02| KT
    |03| LG U+
    |04| 알뜰폰 - SKT
    |05| 알뜰폰 - KT
    |06| 알뜰폰 - LG U+

    partial_update: [유저 프로파일 업데이트]

    ** 이동통신사(mobile_carrier) 코드 정의 ** : [유저 프로파일 조회] 참조

    ci필드의 경우 설정된 값이 있으면 조회만 가능합니다.
    """
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    serializer_action_map = {
        'retrieve': None,
        'partial_update': UserUpdateSerializer
    }
    permission_classes_map = {
        'retrieve': [IsAuthenticated],
    }
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_object(self):
        return self.get_queryset().get()


class RefreshTokenViewSet(viewsets.ModelViewSet):
    queryset = ExpiringToken.objects.all()
    serializer_class = RefreshTokenSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExpiringToken.objects.filter(user__site=get_current_site(self.request))

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, **self.request.data)
        return obj