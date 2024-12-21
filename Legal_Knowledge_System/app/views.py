import os
from django.http import HttpResponse, HttpRequest
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import LawInformation, LocalLawInformation, CaseInformation


# Create your views here.


def index(request: HttpRequest):
    """
    index/
    首页
    """
    return render(request, "index.html")


def login(request: HttpRequest):
    """
    login/
    登录页面
    """
    if request.method == "POST":
        return HttpResponse("Login")
    elif request.method == "GET":
        return render(request, "login.html")
    else:
        return HttpResponse("Method Error")


def doLogin(request: HttpRequest):
    """
    doLogin/
    登录逻辑
    """
    if request.method == "POST":
        return HttpResponse("Login")
    else:
        return HttpResponse("Method Error")


def doRegister(request: HttpRequest):
    """
    doRegister/
    注册逻辑
    """
    if request.method == "POST":
        return HttpResponse("Register")
    else:
        return HttpResponse("Method Error")


def user_detail(request: HttpRequest, user_id):
    """
    user_detail/<str:user_id>/
    用户详情页面
    """
    return HttpResponse(f"Hello, {user_id}")


def ai_chat(request: HttpRequest):
    """
    ai_chat/
    人工智能聊天页面
    """
    return render(request, "chat.html")


def search(request: HttpRequest):
    """
    search/
    搜索页面
    """
    return HttpResponse("Search")


def laws_view(request: HttpRequest):
    """
    laws/
    法律法规页面
    """
    # 参数
    classification = request.GET.get("classification", "宪法")
    status = request.GET.get("status", "")
    search_query = request.GET.get("q", "")
    page = request.GET.get("page", "1")

    context = {
        "domain": os.environ.get("DOMAIN"),
        "all_classifications": ["宪法", "法律", "行政法规", "监察法规", "司法解释", "地方性法规"],
        "all_status": ["", "有效", "已修改", "已废止", "尚未生效"],
        "classification": classification,
        "status": status,
        "search_query": search_query,
        "page": page,
        "laws": [],
    }

    if classification != "地方性法规":
        laws = LawInformation.objects.all().order_by("-name")
    else:
        laws = LocalLawInformation.objects.all().order_by("-name")

    if classification:
        laws = laws.filter(classification=classification)
    if status:
        laws = laws.filter(status=status)
    if search_query:
        laws = laws.filter(name__icontains=search_query)
    paginator = Paginator(laws, 10)
    context["laws"] = paginator.get_page(page)
    context["total_pages"] = paginator.num_pages

    return render(request, "laws.html", context)


def law_detail(request: HttpRequest, classification: str, law_id: str):
    """
    law_detail/<str:classification>/<str:law_id>/
    法律法规详情页面
    """
    table = LocalLawInformation.objects.all() if classification == "地方性法规" else LawInformation.objects.all()
    # 查找id是否存在
    law = table.filter(id=law_id).first()

    if law:
        data = {"domain": os.environ.get("DOMAIN"), "law": law}
        return render(request, "law_detail.html", data)
    else:
        return HttpResponse("Not Found")


def case_view(request: HttpRequest):
    """
    case_view/
    案例查询页面
    """
    # 参数
    classification = request.GET.get("classification", "")
    title = request.GET.get("q", "")
    publish = request.GET.get("publish", "")
    source = request.GET.get("source", "")
    page = request.GET.get("page", "1")

    # 查询
    table = CaseInformation.objects.all().order_by("-title")
    if classification:
        table = table.filter(classification__icontains=classification)
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
        "all_classifications": [
            "",
            "行政指导案例",
            "民事指导案例",
            "刑事指导案例",
            "行政典型案例",
            "民事典型案例",
            "刑事典型案例",
            "行政其他案例",
            "民事其他案例",
            "刑事其他案例",
        ],
        "cases": page_obj,
        "classification": classification,
        "search_query": title,
        "publish": publish,
        "source": source,
    }
    return render(request, "cases.html", data)


def case_detail(request: HttpRequest, classification: str, case_id: str):
    """
    case_detail/<str:classification>/<str:case_id>/
    案例详情页面
    """
    table = CaseInformation.objects.all()
    case = table.filter(id=case_id).first()
    if case:
        case.content = [i.strip() for i in case.content.replace("\n\n", "\n").split("\n")]
        case.content = [f"<b>{line}</b>" if 1 < len(line) <= 8 else line for line in case.content]
        data = {
            "domain": os.environ.get("DOMAIN"),
            "case": case,
            "classification": classification,
        }
        return render(request, "case_detail.html", data)
    else:
        return HttpResponse("Case Not Found")


# api -----------------------------------------------------------------------------------------------------------------------------


def law_file(request: HttpRequest, file_name: str):
    """
    law_file/<str:file_name>
    返回文件
    """
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


def chat(request: HttpRequest):
    def test_():
        test_str = """
# 请输入您的问题

## 例如：我应该如何申请专利？

```python
a=1
```

正常文字

[链接](https://www.baidu.com)

![图片](https://www.baidu.com/img/bd_logo1.png)

[链接](https://www.baidu.com)

[链接](https://www.baidu.com)
"""
        # 前端渲染时图片之后如果还有内容，会导致图片被多次请求，暂未解决
        for i in test_str:
            yield i
            import time

            time.sleep(0.15)

    numbers = test_()
    response = StreamingHttpResponse(numbers, content_type="text/event-stream")
    return response
