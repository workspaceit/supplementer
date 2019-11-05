import re, random, string, hashlib, json
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from adminapp.models import Users, ResetPassword, HandWorker
from serviceapp.serializers.user_serializer import UserSerializer
from django.http import JsonResponse
from django.conf import settings
import io, os
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from adminapp.views.common_views import CommonView
from adminapp.views.helper import LogHelper


class UserProfilePermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False


class UserUploadPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.type == 'admin':
            return True
        elif request.user.is_authenticated and request.method in ['GET', 'PUT', 'PATCH', 'POST']:
            return True
        return False


class UserInfo(APIView):
    permission_classes = (UserProfilePermissions, )

    def get(self, request):
        request.user.avatar = request.user.avatar.url if request.user.avatar else ''
        if request.user.current_activity:
            request.user.current_activity = json.loads(request.user.current_activity)
        if not request.user.is_staff:
            request.user.telephone_office = request.user.handworker.telephone_office
            request.user.telephone_mobile = request.user.handworker.telephone_mobile
            request.user.company_name = request.user.handworker.company_name
            request.user.working_type = request.user.handworker.working_type
        serializer = UserSerializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # def post(self, request, *args, **kwargs ):
    #     try:
    #         partial = kwargs.pop('partial', True)
    #         instance = Users.objects.get(id=request.user.id)
    #         company_name = request.data.pop("company_name", '')
    #         telephone = request.data.pop("telephone", '')
    #         working_type = request.data.pop("working_type", '')
    #         worker_form = {}
    #         if company_name:
    #             worker_form['company_name'] = company_name
    #         if telephone:
    #             worker_form['telephone'] = telephone
    #         if working_type:
    #             worker_form['working_type'] = working_type
    #         HandWorker.objects.filter(user_id=instance.id).update(**worker_form)
    #         updated_data = {}
    #         if 'first_name' in request.data:
    #             updated_data['first_name'] = request.data['first_name']
    #         if 'last_name' in request.data:
    #             updated_data['last_name'] = request.data['last_name']
    #         serializer = UserSerializer(instance, data=updated_data, partial=partial)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.update(instance, updated_data)
    #
    #         if getattr(instance, '_prefetched_objects_cache', None):
    #             # If 'prefetch_related' has been applied to a queryset, we need to
    #             # forcibly invalidate the prefetch cache on the instance.
    #             instance._prefetched_objects_cache = {}
    #         new_serializer_data = dict(serializer.data)
    #         new_serializer_data['avatar'] = CommonView.get_file_path(request.user.avatar)
    #         if not request.user.is_staff:
    #             new_serializer_data['telephone'] = instance.handworker.telephone
    #             new_serializer_data['company_name'] = instance.handworker.company_name
    #             new_serializer_data['working_type'] = json.loads(instance.handworker.working_type)
    #         return Response(new_serializer_data, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         print(e)
    #         response = {
    #             "message": "Something went wrong. please try again"
    #         }
    #         return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordRequestViewSet:

    @api_view(["post"])
    def forget_password(request):
        try:
            response = {}
            email = request.data.pop("email", '')
            users = Users.objects.filter(email=email, is_active=1)
            if users.exists():
                user = users[0]
                current_time = datetime.now()
                expired_date = current_time + timedelta(hours=1)
                reset_code = user.resetpassword_set.filter(already_used=0, expired_at__gt=current_time)
                if reset_code.exists():
                    hash_code = reset_code[0].hash_code
                    ResetPassword.objects.filter(id=reset_code[0].id).update(expired_at=expired_date)
                else:
                    # generate hash code and store
                    key = ''.join(
                        random.choice(string.ascii_letters + string.digits + string.ascii_letters) for _ in
                        range(10)) + str(datetime.now())
                    key = key.encode('utf-8')
                    hash_code = hashlib.sha224(key).hexdigest()
                    ResetPassword(user=user, hash_code=hash_code, expired_at=expired_date).save()
                # base_url = settings.SITE_URL
                base_url = "http://"+request.get_host()
                mail_template = "mails/reset_password.html"
                context = {
                    'base_url': base_url,
                    'key': hash_code
                }
                subject = "Supplementer ::Password Reset"
                to = user.email
                CommonView.sendEmail(request, mail_template, context, subject, to, user.id)
                response['success'] = True
                response['message'] = "A reset password email is sent to you with confirmation link"
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': "Email doesn't found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            LogHelper.efail(e)
            return Response({'success': False, 'message': "Something went wrong."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @api_view(["post"])
    def change_user_password(request):
        try:
            if not request.user.is_authenticated:
                return Response({'success': False, 'message': "User not authorized."},
                                status=status.HTTP_401_UNAUTHORIZED)
            old_password = request.data.pop("old_password", '')
            password = request.data.pop("password", '')
            confirm_password = request.data.pop("confirm_password", '')
            if password != confirm_password:
                return Response({"password": "Passwords did not match"}, status=status.HTTP_400_BAD_REQUEST)
            if request.user.check_password(old_password):
                request.user.set_password(password)
                request.user.save()
            else:
                return Response({"old_password": "Old Passwords did not match"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'success': True, 'message': "Password Change Successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'message': "Something went wrong."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class UploadsView(APIView):
#
#     permission_classes = (UserUploadPermissions, )
#
#     def post(self, request, format=None):
#         response = {}
#         try:
#             avatar = request.FILES.get('avatar')
#             uploaded_image = io.BytesIO(avatar.read())
#             image = Image.open(uploaded_image)
#             old_image = image
#             output_image = io.BytesIO()
#             image.save(output_image, old_image.format)
#             custom_filename = "avatar_" + str(CommonView.getCurrentintTime(request)) + "." + image.format
#             file_path = "public/images/" + custom_filename
#             avatar_url = CommonView.uploadFileToS3(self, output_image, file_path, old_image)
#             if avatar_url['success']:
#                 Users.objects.filter(id=request.user.id).update(avatar=avatar_url['path'])
#                 response['avatar'] = avatar_url['path']
#                 response['message'] = "successfully updated profile image"
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as e:
#             print(e)
#             response = {
#                 "message": "Something went wrong. please try again"
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
