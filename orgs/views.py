from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Organization, OauthToken
from .serializers import OrgSerializer, OAuthSerializer, ExceptionSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from datetime import datetime
import requests
import base64
import json

# Create your views here.
# Redirect root url to google, nothing to do or view here
def home_redirect_view(request):
    response = redirect('https://google.com')
    return response

def register_client(request):
    code = request.GET['code']
    if code is None:
        return HttpResponseBadRequest()
    orginfo = request.GET['state']
    if orginfo is None:
        return HttpResponseBadRequest()
    
    # Decoding base64 string
    decoded_bytes = base64.b64decode(orginfo)
    decoded_str = decoded_bytes.decode('utf-8')

    # Converting the decoded string to a JSON dictionary
    org = json.loads(decoded_str)

    # Prepare org info for api call

    client_name = org['client']
    app_name = org['app']
    client_id = org['client_id']
    client_secret = org['client_secret']
    organization_id = org['organization_id']
    redirect_uri = 'https://your_domain/registerclient'

    # Try the authorization request
    url = f"https://accounts.zoho.com/oauth/v2/token?code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code"

    payload = {}
    headers = {}

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        serializer = ExceptionSerializer(data={'resp': e.response.text})
        return HttpResponse(serializer.data, status=e.response.status_code)

    data = response.json()
    print(data)
    if "error" in data:
        return HttpResponse(data, status=response.status_code)

    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    new_org = Organization.objects.create(name=client_name, application=app_name, organization_id=organization_id, description=client_name)
    org_pk = new_org.pk

    new_oauth = OauthToken.objects.create(org=new_org, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, refresh_token=refresh_token, access_token=access_token, )

    serializer = OAuthSerializer(new_oauth)
    return JsonResponse(serializer.data, status=200)

    #return HttpResponse("<h2>Client created succesfully</h2><h4>You can close this window now<h4>")

class OrgListApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        orgs = Organization.objects.all()
        serializer = OrgSerializer(orgs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OAuthTokenView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_id):
        org = Organization.objects.get(organization_id=org_id)
        oauth_data = OauthToken.objects.get(org=org)
        
        # Check if current token is valid 
        issued = oauth_data.issued
        tz_info = issued.tzinfo
        current = datetime.now(tz_info)
        diff = current - issued

        if diff.seconds > 3300 or oauth_data.access_token == "" or oauth_data.access_token == None:
            # Re-authorize application

            url = f"https://accounts.zoho.com/oauth/v2/token?refresh_token={oauth_data.refresh_token}&client_id={oauth_data.client_id}&client_secret={oauth_data.client_secret}&redirect_uri={oauth_data.redirect_uri}&grant_type=refresh_token"

            payload = {}
            headers = {}

            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                serializer = ExceptionSerializer(data={'resp': e.response.text})
                return Response(serializer.data, status=e.response.status_code)
            
            data = response.json()

            if "error" in data:
                return Response(data, status=response.status_code)

            access_token = data["access_token"]

            # Save the new access token
            oauth_data.access_token = access_token
            oauth_data.save()

        serializer = OAuthSerializer(oauth_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
            
class ForceOauthToken(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, org_id):
        org = Organization.objects.get(organization_id=org_id)
        oauth_data = OauthToken.objects.get(org=org)

        # Authorize application

        url = f"https://accounts.zoho.com/oauth/v2/token?refresh_token={oauth_data.refresh_token}&client_id={oauth_data.client_id}&client_secret={oauth_data.client_secret}&redirect_uri={oauth_data.redirect_uri}&grant_type=refresh_token"

        payload = {}
        headers = {}

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            serializer = ExceptionSerializer(data={'resp': e.response.text})
            return Response(serializer.data, status=e.response.status_code)
        
        data = response.json()

        if "error" in data:
            return Response(data, status=response.status_code)

        access_token = data["access_token"]

        # Save the new access token
        oauth_data.access_token = access_token
        oauth_data.save()

        serializer = OAuthSerializer(oauth_data)
        return Response(serializer.data, status=status.HTTP_200_OK)