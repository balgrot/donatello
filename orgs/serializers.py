# orgs/serializers.py

from rest_framework import serializers
from .models import Organization, OauthToken

class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "application", "organization_id"]

class OAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = OauthToken
        fields = ["access_token"]

class ExceptionSerializer(serializers.Serializer):
    resp = serializers.JSONField()
