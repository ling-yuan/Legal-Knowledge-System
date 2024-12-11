import os
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import LawInformation, LocalLawInformation, CaseInformation

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
        laws = LawInformation.objects.all()
    else:
        laws = LocalLawInformation.objects.all()

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


def read_file(id: str, file_type: str):
    file_name = f"{id}.{file_type}"
    if os.path.exists(os.environ.get("DATA_FILE_FOLDER") + file_name):
        return "存在：" + file_name
    else:
        return "不存在：" + file_name


def law_detail(request: HttpRequest, classification: str, law_id: str):
    table = LocalLawInformation.objects.all() if classification == "地方性法规" else LawInformation.objects.all()
    # 查找id是否存在
    law = table.filter(id=law_id).first()

    if law:
        data = {"domain": os.environ.get("DOMAIN"), "law": law}
        return render(request, "law_detail.html", data)
    else:
        return HttpResponse("Not Found")


def law_file(request: HttpRequest, file_name: str):
    if os.path.exists(os.environ.get("DATA_FILE_FOLDER") + file_name):
        # 返回文件
        if file_name.endswith(".pdf"):
            with open(os.environ.get("DATA_FILE_FOLDER") + file_name, "rb") as f:
                return HttpResponse(f.read(), content_type="application/pdf")
        elif file_name.endswith(".html"):
            with open(os.environ.get("DATA_FILE_FOLDER") + file_name, "r", encoding="utf-8") as f:
                return HttpResponse(f.read(), content_type="text/html; charset=utf-8")
        else:
            with open(os.environ.get("DATA_FILE_FOLDER") + file_name, "rb") as f:
                return HttpResponse(f.read(), content_type="application/octet-stream")
    else:
        return HttpResponse("File Not Found")


def case_view(request: HttpRequest):
    # 参数
    classification = request.GET.get("classification", "行政指导案例")
    title = request.GET.get("title", "")
    publish = request.GET.get("publish", "")
    source = request.GET.get("source", "")
    page = request.GET.get("page", "1")

    # 查询
    table = CaseInformation.objects.all()
    if classification:
        table = table.filter(classification=classification)
    if title:
        table = table.filter(title__icontains=title)
    if publish:
        table = table.filter(publish__icontains=publish)
    if source:
        table = table.filter(source__icontains=source)

    # 分页
    paginator = Paginator(table, 10)
    page_obj = paginator.get_page(page)
    data = {
        "domain": os.environ.get("DOMAIN"),
        "cases": page_obj,
        "classification": classification,
        "title": title,
        "publish": publish,
        "source": source,
    }
    return render(request, "cases.html", data)


def case_detail(request: HttpRequest, classification: str, case_id: str):
    table = CaseInformation.objects.all()
    case = table.filter(id=case_id).first()
    if case:
        case.content = case.content.replace("\n\n", "\n").split("\n")
        # 
        data = {
            "domain": os.environ.get("DOMAIN"),
            "case": case,
            "classification": classification,
        }
        return render(request, "case_detail.html", data)
    else:
        return HttpResponse("Case Not Found")
