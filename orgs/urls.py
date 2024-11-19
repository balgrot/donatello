from django.urls import path, include
from .views import (
    OrgListApiView,
    OAuthTokenView,
    ForceOauthToken
)

urlpatterns = [
    path('orgs', OrgListApiView.as_view()),
    path('token/<str:org_id>', OAuthTokenView.as_view()),
    path('token/f/<str:org_id>', ForceOauthToken.as_view()),
]