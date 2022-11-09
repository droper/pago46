# encoding: utf-8

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
