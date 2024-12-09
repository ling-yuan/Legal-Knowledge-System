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
    # 参数
    classification = request.GET.get("classification", "宪法")
    status = request.GET.get("status", "")
    search_query = request.GET.get("q", "")
    page = request.GET.get("page", "1")

    context = {
        "classification": classification,
        "status": status,
        "search_query": search_query,
        "page": page,
        "laws": [],
    }

    if classification != "地方性法规":
        laws = Law_Information.objects.all()
    else:
        laws = Local_Law_Information.objects.all()

    if classification:
        laws = laws.filter(classification=classification)
    if status:
        laws = laws.filter(status=status)
    if search_query:
        laws = laws.filter(title__icontains=search_query)
    paginator = Paginator(laws, 10)
    context["laws"] = paginator.get_page(page)
    context["total_pages"] = paginator.num_pages

    return render(request, "laws.html", context)


def law_detail(request: HttpRequest, law_id):
    return HttpResponse(f"Law Detail: {law_id}")
