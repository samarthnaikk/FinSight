from rest_framework import serializers


class AIIngestSerializer(serializers.Serializer):
    confidential = serializers.DictField(required=True)
    non_confidential = serializers.DictField(required=True)

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
