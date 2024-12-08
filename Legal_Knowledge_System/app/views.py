from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Law_Information, Local_Law_Information

# Create your views here.


def index(request: HttpRequest):
    return render(request, "index.html")


def login(request: HttpRequest):
    if request.method == "POST":
        return HttpResponse("Login")
    elif request.method == "GET":
        return render(request, "login.html")
    else:
        return HttpResponse("Method Error")


def doLogin(request: HttpRequest):
    if request.method == "POST":
        return HttpResponse("Login")
    else:
        return HttpResponse("Method Error")


def doRegister(request: HttpRequest):
    if request.method == "POST":
        return HttpResponse("Register")
    else:
        return HttpResponse("Method Error")


def user_detail(request: HttpRequest, user_id):
    return HttpResponse(f"Hello, {user_id}")


def laws(request: HttpRequest):
    return HttpResponse("Laws")


def cases(request: HttpRequest):
    return HttpResponse("Cases")


def ai_chat(request: HttpRequest):
    return HttpResponse("AI Chat")


def search(request: HttpRequest):
    return HttpResponse("Search")


def laws_view(request: HttpRequest):
    # 获取筛选参数
    classification = request.GET.get("classification", "")
    status = request.GET.get("status", "")
    search_query = request.GET.get("q", "")

    # 合并两个表的查询结果
    laws = Law_Information.objects.all()
    local_laws = Local_Law_Information.objects.all()

    # 应用筛选
    if classification:
        laws = laws.filter(classification=classification)
        local_laws = local_laws.filter(classification=classification)
    if status:
        laws = laws.filter(status=status)
        local_laws = local_laws.filter(status=status)
    if search_query:
        laws = laws.filter(name__icontains=search_query)
        local_laws = local_laws.filter(name__icontains=search_query)

    # 合并结果并排序
    all_laws = list(laws) + list(local_laws)
    all_laws.sort(key=lambda x: x.publish, reverse=True)

    # 分页
    paginator = Paginator(all_laws, 10)  # 每页显示10条
    page = request.GET.get("page")
    laws_page = paginator.get_page(page)

    return render(request, "laws.html", {"laws": laws_page})


def law_detail(request: HttpRequest, law_id):
    return HttpResponse(f"Law Detail: {law_id}")
