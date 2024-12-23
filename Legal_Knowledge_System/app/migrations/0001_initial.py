# Generated by Django 5.1.4 on 2024-12-11 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuthGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, unique=True)),
            ],
            options={
                "db_table": "auth_group",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthGroupPermissions",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                "db_table": "auth_group_permissions",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("codename", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "auth_permission",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128)),
                ("last_login", models.DateTimeField(blank=True, null=True)),
                ("is_superuser", models.IntegerField()),
                ("username", models.CharField(max_length=150, unique=True)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("email", models.CharField(max_length=254)),
                ("is_staff", models.IntegerField()),
                ("is_active", models.IntegerField()),
                ("date_joined", models.DateTimeField()),
            ],
            options={
                "db_table": "auth_user",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthUserGroups",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                "db_table": "auth_user_groups",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthUserUserPermissions",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                "db_table": "auth_user_user_permissions",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="CaseInformation",
            fields=[
                (
                    "id",
                    models.CharField(
                        db_comment="随机uuid",
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "classification",
                    models.CharField(db_comment="案例分类", max_length=6),
                ),
                ("title", models.CharField(db_comment="标题", max_length=255)),
                ("content", models.TextField(blank=True, db_comment="内容", null=True)),
                (
                    "publish",
                    models.CharField(blank=True, db_comment="发布日期", max_length=255, null=True),
                ),
                (
                    "source",
                    models.CharField(blank=True, db_comment="来源", max_length=255, null=True),
                ),
            ],
            options={
                "db_table": "case_information",
                "db_table_comment": "案例信息表",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoAdminLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("action_time", models.DateTimeField()),
                ("object_id", models.TextField(blank=True, null=True)),
                ("object_repr", models.CharField(max_length=200)),
                ("action_flag", models.PositiveSmallIntegerField()),
                ("change_message", models.TextField()),
            ],
            options={
                "db_table": "django_admin_log",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoContentType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("app_label", models.CharField(max_length=100)),
                ("model", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "django_content_type",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoMigrations",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("app", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("applied", models.DateTimeField()),
            ],
            options={
                "db_table": "django_migrations",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoSession",
            fields=[
                (
                    "session_key",
                    models.CharField(max_length=40, primary_key=True, serialize=False),
                ),
                ("session_data", models.TextField()),
                ("expire_date", models.DateTimeField()),
            ],
            options={
                "db_table": "django_session",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="LawInformation",
            fields=[
                (
                    "id",
                    models.CharField(
                        db_comment="随机uuid",
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "classification",
                    models.CharField(db_comment="法律分类", max_length=5),
                ),
                ("name", models.CharField(db_comment="法律名称", max_length=255)),
                (
                    "office",
                    models.CharField(blank=True, db_comment="制定机关", max_length=255, null=True),
                ),
                (
                    "lawtype",
                    models.CharField(blank=True, db_comment="法律性质", max_length=255, null=True),
                ),
                (
                    "status",
                    models.CharField(blank=True, db_comment="时效性", max_length=255, null=True),
                ),
                (
                    "publish",
                    models.CharField(blank=True, db_comment="公布日期", max_length=255, null=True),
                ),
                (
                    "filetype",
                    models.CharField(blank=True, db_comment="文件类型", max_length=255, null=True),
                ),
            ],
            options={
                "db_table": "law_information",
                "db_table_comment": "宪法、法律、 行政法规、监察法规、司法解释的法律信息表",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="LocalLawInformation",
            fields=[
                (
                    "id",
                    models.CharField(
                        db_comment="随机uuid",
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "classification",
                    models.CharField(db_comment="法律分类", max_length=5),
                ),
                ("name", models.CharField(db_comment="法律名称", max_length=255)),
                (
                    "office",
                    models.CharField(blank=True, db_comment="制定机关", max_length=255, null=True),
                ),
                (
                    "lawtype",
                    models.CharField(blank=True, db_comment="法律性质", max_length=255, null=True),
                ),
                (
                    "status",
                    models.CharField(blank=True, db_comment="时效性", max_length=255, null=True),
                ),
                (
                    "publish",
                    models.CharField(blank=True, db_comment="公布日期", max_length=255, null=True),
                ),
                (
                    "filetype",
                    models.CharField(blank=True, db_comment="文件类型", max_length=255, null=True),
                ),
            ],
            options={
                "db_table": "local_law_information",
                "db_table_comment": "地方性法规的法律信息表",
                "managed": False,
            },
        ),
    ]
