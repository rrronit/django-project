from django.urls import path
from . import views



urlpatterns = [
    path('',views.home,name="home"),
    path('addCourse/',views.addCourse,name="addCourse"),
    path('addCourse/processAddCourse/',views.processAddCourse,name="processAddCourse"),
    path('course/<str:courseId>/', views.course, name='course'),
    path('courses/', views.allCourses, name='allCourse'),
    path('streamUnit/', views.streamUnit, name='allCourse'),
    path('addCourse/<str:courseName>', views.generateCourse, name='allCourse'),
    path("addToDB/",views.addCourseToDB),
    path("getVideoSummary/",views.getVideoSummary),
    path("getVideoQuestions/",views.getVideoQuestions)


]
