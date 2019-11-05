from rest_framework import serializers
from adminapp.models import Comments


class CommentSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=1000)
    type = serializers.CharField(max_length=20)
    file_type = serializers.JSONField()
    user = serializers.SerializerMethodField()
    created_at = serializers.CharField(max_length=100, read_only=True)

    class Meta:
        model = Comments
        fields = ('id', 'text', 'type', 'file_type', 'user', 'created_at')

    def get_user(self, comment):
        if comment.user.is_staff:
            user_info = {
                "name": comment.user.get_full_name(),
                "avatar": comment.user.avatar.url if comment.user.avatar else ''
            }
        else:
            user_info = {
                "name": comment.user.handworker.company_name,
                "avatar": comment.user.avatar.url if comment.user.avatar else ''
            }
        return user_info
