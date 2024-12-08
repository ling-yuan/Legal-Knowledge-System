# Generated by Django 5.1.3 on 2024-12-08 14:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Law_Information",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="随机uuid",
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "classification",
                    models.CharField(
                        choices=[
                            ("宪法", "宪法"),
                            ("法律", "法律"),
                            ("行政法规", "行政法规"),
                            ("监察法规", "监察法规"),
                            ("司法解释", "司法解释"),
                            ("地方性法规", "地方性法规"),
                        ],
                        help_text="法律分类",
                        max_length=20,
                        verbose_name="法律分类",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="法律名称", max_length=255, verbose_name="法律名称"
                    ),
                ),
                (
                    "office",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="制定机关",
                        max_length=255,
                        verbose_name="制定机关",
                    ),
                ),
                (
                    "lawtype",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="法律性质",
                        max_length=255,
                        verbose_name="法律性质",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="时效性",
                        max_length=255,
                        verbose_name="时效性",
                    ),
                ),
                (
                    "publish",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="公布日期",
                        max_length=255,
                        verbose_name="公布日期",
                    ),
                ),
                (
                    "filetype",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="文件类型",
                        max_length=255,
                        verbose_name="文件类型",
                    ),
                ),
            ],
            options={
                "verbose_name": "法律信息",
                "verbose_name_plural": "法律信息",
                "db_table": "Law_Information",
                "ordering": ["-publish"],
            },
        ),
        migrations.CreateModel(
            name="Local_Law_Information",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="随机uuid",
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "classification",
                    models.CharField(
                        choices=[
                            ("宪法", "宪法"),
                            ("法律", "法律"),
                            ("行政法规", "行政法规"),
                            ("监察法规", "监察法规"),
                            ("司法解释", "司法解释"),
                            ("地方性法规", "地方性法规"),
                        ],
                        help_text="法律分类",
                        max_length=20,
                        verbose_name="法律分类",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="法律名称", max_length=255, verbose_name="法律名称"
                    ),
                ),
                (
                    "office",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="制定机关",
                        max_length=255,
                        verbose_name="制定机关",
                    ),
                ),
                (
                    "lawtype",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="法律性质",
                        max_length=255,
                        verbose_name="法律性质",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="时效性",
                        max_length=255,
                        verbose_name="时效性",
                    ),
                ),
                (
                    "publish",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="公布日期",
                        max_length=255,
                        verbose_name="公布日期",
                    ),
                ),
                (
                    "filetype",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="文件类型",
                        max_length=255,
                        verbose_name="文件类型",
                    ),
                ),
            ],
            options={
                "verbose_name": "地方性法规信息",
                "verbose_name_plural": "地方性法规信息",
                "db_table": "Local_Law_Information",
                "ordering": ["-publish"],
            },
        ),
    ]