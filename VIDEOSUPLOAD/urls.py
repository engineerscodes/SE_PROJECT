from django.contrib import admin
from django.urls import path
from . import views
from .views import ajaxsubmitVideo

urlpatterns = [
    path('upload/',views.PUTVD,name="UPLOAD"),
    #path('videos/',views.allVideos,name="gallery"), //deprecated endpoint
    path('videos/<uuid>',views.getSingleVideo,name="Filter Video"),
    path('',views.homePage,name="HOMEPAGE"),
    path('getcontent/',views.getcontent,name="HOME PAGE VIDEO"),
    path('bitdance/moderator/',views.Moderator,name="Moderator's"),
    path('bitdance/GodMode/',views.GodMode,name="Total Marks"),
    path('bitdance/moderator/ajax',views.ajaxModeration,name="GETMODEAJAX"),
    path('upload/ajax',ajaxsubmitVideo.as_view(),name="upload vidoe"), #typo its video
    #path('upload/ajax2', views.ajaxsubmitVideo2, name="GET VIDEO"),
    path('getcontent/filter', views.filters, name="DATE FILTER"),
    path('banner/',views.banner,name="BANNER PAGE"),
    path('events/',views.eventsajax,name="sort by events"),
    path('analaytics/',views.analaytics,name="Analaytics")
]