from rest_framework import serializers
from .models import Email


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = [
            'id', 'sender', 'recipient', 'subject',
            'body', 'created_at', 'is_read', 'folder'
        ]
        read_only_fields = ['id', 'created_at', 'is_read']
        extra_kwargs = {
            'sender': {'required': True},
            'recipient': {'required': True},
            'subject': {'required': True},
            'body': {'required': True},
        }
