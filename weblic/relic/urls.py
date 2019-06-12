# relic/urls.py
from django.conf.urls import url
from relic import views


urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),
]