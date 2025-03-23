"""
URL configuration for Legal_Knowledge_System project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("doLogin/", views.doLogin, name="doLogin"),
    path("doRegister/", views.doRegister, name="doRegister"),
    path("logout/", views.logout, name="logout"),
    path("user_detail/<str:uname>/", views.user_detail, name="user_detail"),
    path("ai_chat/", views.ai_chat, name="ai_chat"),
    path("search/", views.case_view, name="search"),
    path("laws/", views.laws_view, name="laws"),
    path("law_detail/<str:classification>/<str:law_id>/", view=views.law_detail, name="law_detail"),
    path("cases/", views.case_view, name="cases"),
    path("case_detail/<str:classification>/<str:case_id>/", view=views.case_detail, name="case_detail"),
    # 法律文书模板
    path("document_templates/", views.document_templates_view, name="document_templates"),
    path(
        "document_template_detail/<str:template_id>/", views.document_template_detail, name="document_template_detail"
    ),
    # api
    path("law_file/<str:file_name>", view=views.law_file, name="law_file"),
    path("api/chat/", views.chat, name="chat"),
    path("api/chat/history/clear/", views.clear_history, name="clear_history"),
]
