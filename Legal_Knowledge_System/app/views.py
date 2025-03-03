import json
import os
from django.http import HttpResponse, HttpRequest
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import LawInformation, LocalLawInformation, CaseInformation
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from .utils import check_login
from legal_chatbot import legal_bot, legal_bot_thinking

bot = legal_bot_thinking()
# Create your views here.


def index(request: HttpRequest):
    """
    index/
    首页
    """
    uname = request.session.get("uname", "")
    return render(request, "index.html", {"uname": uname})


def login(request: HttpRequest):
    """
    login/
    登录页面
    """
    t = {
        "showLogin": True if request.GET.get("showLogin", True) == "1" else False,
        "massages": messages.get_messages(request),
    }
    return render(request, "login.html", t)


def doLogin(request: HttpRequest):
    """
    doLogin/
    登录逻辑
    """
    if request.method == "POST":
        # uname = request.POST.get("uname", "")
        uemail = request.POST.get("uemail", "")
        upwd = request.POST.get("upwd", "")
        # 根据email查询用户
        user = User.objects.filter(email=uemail).first()
        if user:
            uname = user.username
            user = authenticate(password=upwd, username=uname)
            if user:
                auth_login(request, user)
                request.session["uname"] = user.username
                # messages.success(request, "登录成功")
                return redirect("index")
            else:
                messages.error(request, "用户名或密码有误")
                return redirect("/login/?showLogin=1")
        else:
            messages.error(request, "用户不存在，请先注册")
            return redirect("/login/?showLogin=1")
    else:
        return HttpResponse("Method Error")


def doRegister(request: HttpRequest):
    """
    doRegister/
    注册逻辑
    """
    if request.method == "POST":
        uname = request.POST.get("uname", "")
        uemail = request.POST.get("uemail", "")
        upwd = request.POST.get("upwd", "")
        if uname == "" or uemail == "" or upwd == "":
            messages.error(request, "用户名、邮箱或密码均不能为空")
            return redirect("/login/?showLogin=0")
        if User.objects.filter(email=uemail).exists():
            messages.error(request, "邮箱已被使用")
            return redirect("/login/?showLogin=0")
        elif User.objects.filter(username=uname).exists():
            messages.error(request, "用户名已被使用")
            return redirect("/login/?showLogin=0")
        user = User.objects.create_user(username=uname, email=uemail, password=upwd)
        user.save()
        if user:
            auth_login(request, user)
            request.session["uname"] = user.username
            # messages.success(request, "登录成功")
            return redirect("index")
        else:
            messages.error(request, "注册失败")
            return redirect("/login/?showLogin=0")
    else:
        return HttpResponse("Method Error")


@check_login
def logout(request: HttpRequest):
    """
    logout/
    登出逻辑
    """
    auth_logout(request)
    return redirect("index")


@check_login
def user_detail(request: HttpRequest, uname):
    """
    user_detail/<str:uname>/
    用户详情页面
    """
    user = User.objects.filter(username=uname).first()
    if user:
        context = {
            "user": user,
            "uname": request.session.get("uname", ""),
        }
        return render(request, "user_detail.html", context)
    else:
        return HttpResponse("User Not Found")


@check_login
def ai_chat(request: HttpRequest):
    """
    ai_chat/
    人工智能聊天页面
    """
    uname = request.session.get("uname", "")
    data = bot.chat_history.store.get(uname, None)
    # data = legal_bot().store.get(uname, None)
    chat_history = []
    if data:
        for n, i in enumerate(data.messages):
            chat_history.append(
                {
                    "role": n % 2 == 0 and "user" or "bot",
                    "content": i.content,
                }
            )
    return render(
        request,
        "chat.html",
        {
            "uname": uname,
            "chat_history": chat_history,
        },
    )


@check_login
def search(request: HttpRequest):
    """
    search/
    搜索页面
    """
    return HttpResponse("Search")


@check_login
def laws_view(request: HttpRequest):
    """
    laws/
    法律法规页面
    """
    # 获取用户
    uname = request.session.get("uname", "")
    # 参数
    classification = request.GET.get("classification", "宪法")
    status = request.GET.get("status", "")
    search_query = request.GET.get("q", "")
    page = request.GET.get("page", "1")

    context = {
        "uname": uname,
        "domain": os.environ.get("DOMAIN"),
        "all_classifications": ["宪法", "法律", "行政法规", "监察法规", "司法解释", "民法典", "地方性法规"],
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


@check_login
def law_detail(request: HttpRequest, classification: str, law_id: str):
    """
    law_detail/<str:classification>/<str:law_id>/
    法律法规详情页面
    """
    # 获取用户
    uname = request.session.get("uname", "")
    table = LocalLawInformation.objects.all() if classification == "地方性法规" else LawInformation.objects.all()
    # 查找id是否存在
    law = table.filter(id=law_id).first()

    if law:
        data = {"domain": os.environ.get("DOMAIN"), "law": law, "uname": uname}
        return render(request, "law_detail.html", data)
    else:
        return HttpResponse("Not Found")


@check_login
def case_view(request: HttpRequest):
    """
    case_view/
    案例查询页面
    """
    # 获取用户
    uname = request.session.get("uname", "")
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
        "uname": uname,
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


@check_login
def case_detail(request: HttpRequest, classification: str, case_id: str):
    """
    case_detail/<str:classification>/<str:case_id>/
    案例详情页面
    """
    # 获取用户
    uname = request.session.get("uname", "")
    table = CaseInformation.objects.all()
    case = table.filter(id=case_id).first()
    if case:
        case.content = [i.strip() for i in case.content.replace("\n\n", "\n").split("\n")]
        case.content = [f"<b>{line}</b>" if 1 < len(line) <= 8 else line for line in case.content]
        data = {
            "uname": uname,
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


@check_login
def chat(request: HttpRequest):
    # 所有参数
    if request.method == "POST":
        uname = request.session.get("uname", "")
        body = request.body.decode("utf-8")
        data = json.loads(body)
        q = data.get("question", None)
        answer = bot.stream(q, uname)
        # answer = legal_bot().stream(q, uname)
        response = StreamingHttpResponse(answer, content_type="text/event-stream")
        return response
    else:
        return HttpResponse("Method Not Allowed")


@check_login
def clear_history(request: HttpRequest):
    # 所有参数
    if request.method == "POST":
        uname = request.session.get("uname", "")
        bot.chat_history.remove_session(uname)
        return HttpResponse("ok")
    else:
        return HttpResponse("Method Not Allowed")
