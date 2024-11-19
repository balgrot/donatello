from django.db import models

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=50)
    application = models.CharField(max_length=50)
    organization_id = models.CharField(max_length=50,unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name + ' ' + self.application + ' ' + self.organization_id

class OauthToken(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=50)
    redirect_uri = models.CharField(max_length=100)
    refresh_token = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100,null=True,blank=True)
    issued = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.org.name + ' '  + self.org.application + ' ' + self.org.organization_id