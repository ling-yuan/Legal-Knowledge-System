import uuid
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_groups"
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_user_permissions"
        unique_together = (("user", "permission"),)


class CaseInformation(models.Model):
    id = models.CharField(primary_key=True, max_length=255, db_comment="随机uuid")
    classification = models.CharField(max_length=6, db_comment="案例分类")
    title = models.CharField(max_length=255, db_comment="标题")
    content = models.TextField(blank=True, null=True, db_comment="内容")
    publish = models.CharField(max_length=255, blank=True, null=True, db_comment="发布日期")
    source = models.CharField(max_length=255, blank=True, null=True, db_comment="来源")

    class Meta:
        managed = False
        db_table = "case_information"
        db_table_comment = "案例信息表"


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class LawInformation(models.Model):
    id = models.CharField(primary_key=True, max_length=255, db_comment="随机uuid")
    classification = models.CharField(max_length=5, db_comment="法律分类")
    name = models.CharField(max_length=255, db_comment="法律名称")
    office = models.CharField(max_length=255, blank=True, null=True, db_comment="制定机关")
    lawtype = models.CharField(max_length=255, blank=True, null=True, db_comment="法律性质")
    status = models.CharField(max_length=255, blank=True, null=True, db_comment="时效性")
    publish = models.CharField(max_length=255, blank=True, null=True, db_comment="公布日期")
    filetype = models.CharField(max_length=255, blank=True, null=True, db_comment="文件类型")

    class Meta:
        managed = False
        db_table = "law_information"
        db_table_comment = "宪法、法律、 行政法规、监察法规、司法解释的法律信息表"


class LocalLawInformation(models.Model):
    id = models.CharField(primary_key=True, max_length=255, db_comment="随机uuid")
    classification = models.CharField(max_length=5, db_comment="法律分类")
    name = models.CharField(max_length=255, db_comment="法律名称")
    office = models.CharField(max_length=255, blank=True, null=True, db_comment="制定机关")
    lawtype = models.CharField(max_length=255, blank=True, null=True, db_comment="法律性质")
    status = models.CharField(max_length=255, blank=True, null=True, db_comment="时效性")
    publish = models.CharField(max_length=255, blank=True, null=True, db_comment="公布日期")
    filetype = models.CharField(max_length=255, blank=True, null=True, db_comment="文件类型")

    class Meta:
        managed = False
        db_table = "local_law_information"
        db_table_comment = "地方性法规的法律信息表"
