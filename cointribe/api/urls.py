from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token
from . import views


urlpatterns = [
    url(r'^v1/login$', views.Login.as_view()),
    url(r'^v1/inventory$',views.InventoryList.as_view()),
    url(r'^v1/inventory/(?P<pk>[0-9]+)/$',views.InventoryDetail.as_view()),
    url(r'^v1/inventoryAproved$',views.ApprovModel.as_view()),
    url(r'^v1/inventoryAproved/(?P<pk>[0-9]+)/$',views.ApprovModel.as_view()),
    url(r'^api-token-auth/', obtain_auth_token),
]