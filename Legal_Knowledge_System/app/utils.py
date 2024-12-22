from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect


def check_login(func):
    """
    检查登陆状态
    """

    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.session.get("uname", None):
            return func(request, *args, **kwargs)
        else:
            return redirect("/login")

    return wrapper
