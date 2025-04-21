from django.urls import path
from . import views

urlpatterns = [
    path('set-aws-creds/', views.set_aws_creds),
    path('permissions/', views.get_permissions),
    # path('ec2/list/', views.list_instances),
    # path('ec2/launch/', views.launch_instance),
    # path('ec2/terminate/', views.terminate_instance),
]
