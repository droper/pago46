"""pago46 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from debts.schema import schema
from debts.views import SettleUpView, AddUserView, CreateIOUView

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("expired_iou", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path("settleup", SettleUpView.as_view(), name="settleup"),
    path("add", AddUserView.as_view(), name="add"),
    path("iou", CreateIOUView.as_view(), name="iou"),
]
