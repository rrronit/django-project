from django.shortcuts import render,redirect,HttpResponse
from django.http import StreamingHttpResponse,JsonResponse
from django.contrib import messages
from utils.strict_gpt import process_prompt
from utils.getImage import getImage
from utils.generateMCQ import generateQuestion
from utils.searchYoutube import searchYoutube,getCaption
import concurrent.futures
from django.views.decorators.csrf import csrf_exempt
from .models import Course,Unit,Chapter,Question
import time 
import json
from uuid import uuid4

courses=[]

def home(req):
    return render(req,'home.html',{}) 

def allCourses(req):
    courses=Course.objects.all()
    allCourses=[]
    for course in courses:
        course={
            "id":course.id,
            "image":course.image,
            "name":course.name
        }
        allCourses.append(course)

    return render(req,"courses.html",{"courses":allCourses})

def addCourse(req): 
    return render(req,"addCourse.html",{})

def processAddCourse(req):
    data=json.loads(req.body.decode("utf-8"))
    courseName=data.get("courseName")
    unitNames=data.get("units")
    req.session["courseName"]=courseName
    courses.append((courseName,unitNames))
    return JsonResponse({"message":"done"})


    """ units=[]    
    for unit in unitNames:
        prompt="It is your job to create a course about "+unit+", the User has requested to create chapters for each of the units. Then for each chapter, provide a detailed youtube search query that can be used to find informative educational video for each chapter. Each query should give an educational informative course in youtube"
        units.append(prompt)
        
    with concurrent.futures.ThreadPoolExecutor() as exc:
   

        res=[exc.submit(process_prompt,)for prompt in units]

        for f in concurrent.futures.as_completed(res):
            yield f.result()
    """

def streamUnit(req):
    if (len(courses)!=0):
        courseName=courses[0][0]
        unitNames=courses[0][1]
        units=[]
        for unit in unitNames:
            prompt="The User wants to pursue "+ courseName +"It is your job to create a course only about "+unit+", the User has requested to create chapters for each of the units. Then for each chapter, provide a detailed youtube search query that can be used to find informative educational video for each chapter. Each query should give an educational informative course in youtube"
            units.append(prompt)
        
   
        courses.pop(0)

        res=StreamingHttpResponse(streamHelper(units),content_type="text/event-stream")
        
        return res
    return render(req,"addCourse.html")

def streamHelper(units):

    with concurrent.futures.ThreadPoolExecutor() as exc:
        res=[exc.submit(process_prompt,prompt) for prompt in units]
        for f in concurrent.futures.as_completed(res):
            
            data=json.loads(f.result().replace("'",'"'))
            print(data)
            title=data["title"]
            chapters=data["chapters"]    
            yield f"data:{json.dumps({'title': title, 'chapters': chapters})}\n\n"
        

def generateCourse(req,courseName):
    return render(req,"generateCourse.html",{"courseName":courseName})


def course(req,courseId):

    
    course=Course.objects.get(id=courseId)
    units=Unit.objects.filter(courseId=course.id)
        
 
    courseData={}
    courseData["title"]=course.name
    courseData["units"]=[]
    

    for unit in units:
        unitData={}
        unitData["title"]=unit.name
        unitData["chapters"]=[]
        chapters=Chapter.objects.filter(unitId=unit.id)
        for chapter in chapters:
            
            chapterData={}
            chapterData["Id"]=chapter.id
            chapterData["title"]=chapter.name
            chapterData["youtubeQuery"]=chapter.youtubeSearchQuery
            chapterData["videoId"]=chapter.videoId
            unitData["chapters"].append(chapterData)

                

        courseData["units"].append(unitData)
            


    return render(req,"course.html",{"course":courseData})



@csrf_exempt
def addCourseToDB(req):
    

    data=json.loads(req.body.decode("utf-8"))
    courseName=data["courseName"]
    units=data["unitData"]
    if (courseName==""):
        return HttpResponse("{'mes':'Not found'}",status=400)
    if (len(units)!=3):

        return HttpResponse('{"mes":"Not found"}',status=400)
  
    print("here")
    courseImg=getImage(courseName)
    course=Course(id=str(uuid4()),name=courseName.capitalize(),image=courseImg)
    course.save()
    
    for unit in units:
        newUnit=Unit(id=str(uuid4()),name=unit["title"],courseId=course.id,course=course)
        newUnit.save()

        for chapter in unit["chapters"]:
            newChapter=Chapter(id=uuid4(),unitId=newUnit.id,name=chapter["title"],youtubeSearchQuery=chapter["youtube_query"],unit=newUnit)
            newChapter.save()
            
        with concurrent.futures.ThreadPoolExecutor() as exc:
            print(Chapter.objects.filter(unit=newUnit))
            res=[exc.submit(searchYoutube,chapter) for chapter in Chapter.objects.filter(unitId=newUnit.id)]
            for f in concurrent.futures.as_completed(res):
                print(f.result())
                
            
    
        
    
    return JsonResponse({"courseID":course.id})
    
    
    

@csrf_exempt
def getVideoSummary(req):
    chapterId=req.body.decode("utf-8")
    chapter=Chapter.objects.get(id=chapterId)
    

    
    
    if (chapter.summary):
        return JsonResponse({"summary":chapter.summary})
    
    chapter.summary=getCaption(chapter.videoId)
    chapter.save()

    return JsonResponse({"summary":chapter.summary})




@csrf_exempt
def getVideoQuestions(req):
    chapterId=req.body.decode("utf-8")
    chapter=Chapter.objects.get(id=chapterId)
    questions=Question.objects.filter(chapterId=chapter.id)

    
    if (questions):
        jsonQuestion=[]
        for question in questions:
            data={
                "question":question.question,
                "options":question.options,
                "answer":question.answer
            }
            jsonQuestion.append(data)

        return JsonResponse({"questions":jsonQuestion})

    generatedQuestions=generateQuestion(chapter.summary) 

    if (generatedQuestions==None):
        return JsonResponse({"message":"Failed"},status=400)
    
     
    for question in generatedQuestions:
        question=Question(id=str(uuid4()),chapterId=chapter.id,question=question["question"],answer=question["answer"],options=question["options"],chapter=chapter) 
        question.save()

    questions=Question.objects.filter(chapter=chapter)
    
    jsonQuestion=[]
    for question in questions:
        data={
            "question":question.question,
            "options":question.options,
            "answer":question.answer
        }
        jsonQuestion.append(data)
    return JsonResponse({"questions":jsonQuestion})


    