from django.contrib import admin
from orgs.models import Organization
from orgs.models import OauthToken
# Register your models here.

admin.site.register(Organization)
admin.site.register(OauthToken)