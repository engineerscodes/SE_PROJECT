from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from rest_framework import status

from .forms import vd_form
from .models import videoUpload, Marks
from datetime import date
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.views import APIView
from django.utils.encoding import force_text, force_bytes
from django.apps import apps
# from django.http import JsonResponse
# from django.db.models import Q
from .serializers import videoUploadSerializer, MarksSerializer, SubmitVideo, VDContent, EventSerial
from rest_framework.response import Response
from rest_framework.decorators import api_view
# from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
import re

Mode = apps.get_model('Moderator', 'Mode')
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

# from Event.forms import EventForm  #pycharme bug it not error
Events = apps.get_model('Event', 'Event')


# upload page start
def PUTVD(request):
    if request.method == "GET":
        user = request.user
        if (user.is_authenticated == False):
            return redirect('/account/login')

        form = vd_form()
        # event=Events.objects.filter(lastDate__lte=date.today().strftime('%Y-%m-%d'))
        try:
            event = Events.objects.filter(lastDate__gte=date.today().strftime('%Y-%m-%d'))
        except Exception as e:
            event = None  # filter will not through exceptions
        return render(request, "upload.html", {"form": form, "event": event})
    else:
        return redirect('/account/login')


class ajaxsubmitVideo(APIView):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    def post(self, request, format=None):

        user = request.user
        if (user.is_authenticated):
            serializerss = SubmitVideo(data=request.data)
            # print(request.POST.get('captions'))

            if serializerss.is_valid():
                # print(serializerss.validated_data[''])
                # print(request.POST['events'])
                form = vd_form(data=request.POST, files=request.FILES)
                if form.is_valid():
                    if re.search('^https:\/\/www\.youtube\.com\/watch\?v=.{11}$', request.POST['video']) is None:
                        return Response("Invalid Url ,Only Youtube url allowed ", status=status.HTTP_400_BAD_REQUEST)
                    else:
                        try:

                            check_vd = videoUpload.objects.get(username=request.user.email,
                                                               EventName=request.POST['events'])
                            check_vd.date = date.today().strftime('%Y-%m-%d')
                            check_vd.video = request.POST['video']
                            check_vd.captions = request.POST['captions']
                            check_vd.Total_marks = 0
                            check_vd.save()
                            Marks.objects.filter(videoId=check_vd.id).delete()
                            return Response("VIDEO OVERRIDDEN ", status=status.HTTP_200_OK)
                        except:
                            new_form = form.save(commit=False)
                            new_form.username = request.user.email
                            new_form.date = date.today().strftime('%Y-%m-%d')
                            new_form.save()
                            video = videoUpload.objects.get(pk=new_form.id)
                            video.url_64encoding = urlsafe_base64_encode(force_bytes(new_form.id))
                            # video.thumbnail = serializerss.validated_data['thumbnail']
                            try:
                                event = Events.objects.get(eventname=request.POST['events'],
                                                           lastDate__gte=date.today().strftime('%Y-%m-%d'))
                                video.EventName = event.eventname
                                video.save()
                            except Exception as e:
                                return Response("Event doesn't Exist", status=status.HTTP_400_BAD_REQUEST)

                            return Response("VIDEO | UPLOADED", status=status.HTTP_200_OK)
            else:
                return Response(serializerss.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data="access denied", status=status.HTTP_400_BAD_REQUEST)


# upload page end

#get allvideos links
def allVideos(request):
    if request.user.is_authenticated == False:
        return redirect('/account/login')
    if not request.user.is_staff:
        return redirect('/')
    if request.method == 'GET':
        allmp4 = videoUpload.objects.all()
        return render(request, 'gallery.html', {'data': allmp4})

#get single video using id
def getSingleVideo(request, uuid):
    if (request.user.is_authenticated == False):
        return redirect('/account/login')
    if request.method == 'GET':
        try:
            id = force_text(urlsafe_base64_decode(uuid))
            video = videoUpload.objects.get(pk=id)

        except Exception:
            video = None

        if video is not None:
            try:
                # print(request.user.email)
                # mode_team = Mode.objects.get(email=request.user.email)
                mode_team = Mode.objects.get(email=request.user)
            except Exception:
                mode_team = None
            if mode_team is not None and mode_team.mode_active:
                current_video_marks = Marks.objects.filter(videoId=id)
                # print(current_video_marks,'###################################')
                return render(request, 'video.html', {'data': video, 'MODES': True, 'Marks': current_video_marks})
            elif request.user.is_staff:
                current_video_marks = Marks.objects.filter(videoId=id)
                return render(request, 'video.html', {'data': video, 'MODES': False, 'Marks': current_video_marks})
            else:
                return render(request, 'video.html', {'data': video, 'MODES': False})
        else:
            return redirect('/videos/')

    if request.method == 'POST':
        try:
            id_post = force_text(urlsafe_base64_decode(uuid))
            video_post = videoUpload.objects.get(pk=id_post)
        except Exception:
            video_post = None
        if request.POST['video_marks'] == '':
            return redirect(f'/videos/{uuid}')

        try:
            neg = int(request.POST['video_marks'])
            if neg < 0:
                messages.info(request, "MARKS CANNOT BE LESS THAN ZERO")
                return redirect(f'/videos/{uuid}')
        except ValueError:
            messages.info(request, "NO STRING ALLOWED")
            return redirect(f'/videos/{uuid}')

        try:
            currentEvent = Events.objects.get(eventname=video_post.EventName)
            if int(request.POST['video_marks']) > currentEvent.maxMarks:
                messages.info(request, f"MAX MARK FOR THIS EVENT IS {currentEvent.maxMarks}")
                return redirect(f'/videos/{uuid}')
        except Exception as e:
            currentEvent = None
            return redirect(f'/videos/{uuid}')
        if video_post != None and request.POST['video_marks'] != '':
            try:
                check_marks = Marks.objects.get(videoId=id_post, moderator_email=request.user.email)
                # print(video_post.total_marks())

            except Exception:
                check_marks = None
            if check_marks is not None and neg >= 0:
                # print(neg,'$$$$$$$$$$$$$$$$',check_marks.marks)
                video_post.Total_marks = int(video_post.Total_marks) + (int(-check_marks.marks) + neg)
                # print(video_post.total_marks(),"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",video_post.Total_marks)
                video_post.save()
                check_marks.marks = request.POST['video_marks']
                check_marks.date = date.today().strftime('%Y-%m-%d')
                check_marks.save()
                return redirect(f'/videos/{uuid}')
            if check_marks is None and neg >= 0:
                video_post.Total_marks = int(video_post.Total_marks) + neg
                # print(video_post.total_marks(),"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                video_post.save()
                video_marks = Marks()

                video_marks.videoId = id_post
                video_marks.video_link = uuid
                video_marks.by_email = video_post.username

                video_marks.moderator_email = request.user.email
                video_marks.date = date.today().strftime('%Y-%m-%d')
                video_marks.marks = request.POST['video_marks']
                video_marks.EventName = video_post.EventName
                video_marks.verfiyed = True
                video_marks.save()
                return redirect(f'/videos/{uuid}')
        else:
            return redirect('/videos')


'''from moviepy.editor import *
clip = VideoFileClip("example.mp4")
clip=clip.resize(width=800)
clip.save_frame("thumbnail.jpg",t=0.10)'''


# HOMEPAGE start here
def homePage(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            # videos = videoUpload.objects.all()
            return render(request, 'HomePage.html')
        else:
            return redirect('/account/login')

#api to get video files - infinite scroll
@api_view(['GET'])
def getcontent(request):
    if request.method == 'GET':
        if request.is_ajax() and request.user.is_authenticated:
            try:
                index = int(request.GET.get('vdreq'))
            except:
                return Response("EXCEPTION HAPPENED", status=status.HTTP_400_BAD_REQUEST)
            allcontent = videoUpload.objects.order_by('date').reverse()[6 * (index - 1):6 * index]
            videofile = VDContent(allcontent, many=True)
            return Response({"data": videofile.data})
        else:
            return Response("PLZ AUTHENTICATE AND CALL MUST BE AJAX", status=status.HTTP_400_BAD_REQUEST)

#API tom get video in that Range of date
@api_view(['GET'])
def filters(request):
    if request.method == 'GET':
        if request.is_ajax() and request.user.is_authenticated:
            print(request.GET.get('fromdate'))
            print(request.GET.get('todate'))
            fromdate = request.GET.get('fromdate')
            todate = request.GET.get('todate')
            allcontent = videoUpload.objects.filter(date__range=[fromdate, todate])
            videofile = VDContent(allcontent, many=True)
            return Response({"data": videofile.data}, status=status.HTTP_200_OK)
        else:
            return Response("PLZ AUTHENTICATE AND CALL MUST BE AJAX", status=status.HTTP_400_BAD_REQUEST)


# HOMEPAGE start ENDS

def Moderator(request):
    if (request.user.is_authenticated == False):
        return redirect('/account/login')
    if request.method == 'GET':

        try:
            # mode_team = Mode.objects.get(email=request.user.email)
            mode_team = Mode.objects.get(email=request.user)
        except Exception:
            mode_team = None

        if mode_team is not None and mode_team.mode_active:
            allmark_user = Marks.objects.filter(moderator_email=request.user.email)
            allmark_user_id = allmark_user.values_list('videoId')

            left_out_video = videoUpload.objects.exclude(pk__in=allmark_user_id)

            return render(request, 'allmarks.html', {'marks': allmark_user, 'LeftOver': left_out_video})
        if request.user.is_staff:
            return redirect('/videos')
        else:
            return redirect('/')
        # return HttpResponse("MODERATIONS")


def GodMode(request):
    if (request.user.is_authenticated == False):
        return redirect('/account/login')
    if request.method == 'GET' and request.user.is_staff:
        Allvideo_mod = videoUpload.objects.order_by('Total_marks').reverse()

        return render(request, 'getmarks.html', {'data': Allvideo_mod})
    if request.method == 'GET':
        return redirect('/videos')


#API TO GET CHECKED AND UNCHECKE VIDEO for MODERATOR
@api_view(['GET'])
def ajaxModeration(request):
    if request.method == 'GET':

        try:
            # mode_team = Mode.objects.get(email=request.user.email)
            mode_team = Mode.objects.get(email=request.user)
        except Exception:
            mode_team = None

        if mode_team is not None and mode_team.username == request.user.username and mode_team.mode_active:
            allmark_user = Marks.objects.filter(moderator_email=request.user.email)
            allmark_user_id = allmark_user.values_list('videoId')
            if request.is_ajax():
                if request.GET['videos'] == "verified":
                    cur_marked = MarksSerializer(allmark_user, many=True)
                    return Response({"data": cur_marked.data})
                if request.GET['videos'] == "unseen":
                    left_out_video = videoUpload.objects.exclude(pk__in=allmark_user_id)
                    left_cur_marked = videoUploadSerializer(left_out_video, many=True)
                    return Response({"data": left_cur_marked.data})
        else:
            return Response({"data": "Access DENIED "}, status=status.HTTP_400_BAD_REQUEST)


#API TO GET VIDEO FOR MODERATORS BY EVENT NAME
@api_view(['GET'])
def eventsajax(request):
    if request.method == 'GET':

        try:
            # mode_team = Mode.objects.get(email=request.user.email)
            mode_team = Mode.objects.get(email=request.user)
        except Exception:
            mode_team = None

        if mode_team is not None and mode_team.username == request.user.username and mode_team.mode_active:
            allmark_user = Marks.objects.filter(moderator_email=request.user.email).order_by('EventName')
            if request.is_ajax():
                cur_marked = MarksSerializer(allmark_user, many=True)
                return Response({"data": cur_marked.data})

        else:
            return Response({"data": "Access DENIED "}, status=status.HTTP_400_BAD_REQUEST)


def banner(request):
    if request.method == "GET":
        return render(request, 'Banner.html')

#API FOR ANALAYTICES FOR MODERATOR
@api_view(['GET'])
def analaytics(request):
    if request.method == 'GET':

        try:
            # mode_team = Mode.objects.get(email=request.user.email)
            mode_team = Mode.objects.get(email=request.user)
        except Exception:
            mode_team = None

        if mode_team is not None and mode_team.username == request.user.username and mode_team.mode_active:
            correct = Marks.objects.filter(moderator_email=request.user.email)
            correct_count = correct.count()
            # Left_count=Marks.objects.exclude(moderator_email=request.user.email).count()
            allmark_user_id = correct.values_list('videoId')
            left_out_video = videoUpload.objects.exclude(pk__in=allmark_user_id)
            Left_count = left_out_video.count()
            if request.is_ajax():
                return Response({"Left_count": Left_count, "Actual_corrected": correct_count})

        else:
            return Response({"data": "Access DENIED "}, status=status.HTTP_400_BAD_REQUEST)
