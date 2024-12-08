import uuid
from django.db import models


class Law_Information(models.Model):
    """宪法、法律、行政法规、监察法规、司法解释的法律信息表"""

    # 法律分类选项
    CLASS_CHOICES = [
        ("宪法", "宪法"),
        ("法律", "法律"),
        ("行政法规", "行政法规"),
        ("监察法规", "监察法规"),
        ("司法解释", "司法解释"),
        ("地方性法规", "地方性法规"),
    ]

    id = models.CharField(
        primary_key=True, max_length=255, default=uuid.uuid4, editable=False, verbose_name="ID", help_text="随机uuid"
    )
    classification = models.CharField(
        max_length=20, choices=CLASS_CHOICES, verbose_name="法律分类", help_text="法律分类"
    )
    name = models.CharField(max_length=255, verbose_name="法律名称", help_text="法律名称")
    office = models.CharField(max_length=255, blank=True, default="", verbose_name="制定机关", help_text="制定机关")
    lawtype = models.CharField(max_length=255, blank=True, default="", verbose_name="法律性质", help_text="法律性质")
    status = models.CharField(max_length=255, blank=True, default="", verbose_name="时效性", help_text="时效性")
    publish = models.CharField(max_length=255, blank=True, default="", verbose_name="公布日期", help_text="公布日期")
    filetype = models.CharField(max_length=255, blank=True, default="", verbose_name="文件类型", help_text="文件类型")

    class Meta:
        db_table = "Law_Information"
        verbose_name = "法律信息"
        verbose_name_plural = "法律信息"
        ordering = ["-publish"]  # 按发布日期倒序排序

    def __str__(self):
        return self.name


class Local_Law_Information(models.Model):
    """地方性法规的法律信息表"""

    # 法律分类选项
    CLASS_CHOICES = [
        ("宪法", "宪法"),
        ("法律", "法律"),
        ("行政法规", "行政法规"),
        ("监察法规", "监察法规"),
        ("司法解释", "司法解释"),
        ("地方性法规", "地方性法规"),
    ]

    id = models.CharField(
        primary_key=True, max_length=255, default=uuid.uuid4, editable=False, verbose_name="ID", help_text="随机uuid"
    )
    classification = models.CharField(
        max_length=20, choices=CLASS_CHOICES, verbose_name="法律分类", help_text="法律分类"
    )
    name = models.CharField(max_length=255, verbose_name="法律名称", help_text="法律名称")
    office = models.CharField(max_length=255, blank=True, default="", verbose_name="制定机关", help_text="制定机关")
    lawtype = models.CharField(max_length=255, blank=True, default="", verbose_name="法律性质", help_text="法律性质")
    status = models.CharField(max_length=255, blank=True, default="", verbose_name="时效性", help_text="时效性")
    publish = models.CharField(max_length=255, blank=True, default="", verbose_name="公布日期", help_text="公布日期")
    filetype = models.CharField(max_length=255, blank=True, default="", verbose_name="文件类型", help_text="文件类型")

    class Meta:
        db_table = "Local_Law_Information"
        verbose_name = "地方性法规信息"
        verbose_name_plural = "地方性法规信息"
        ordering = ["-publish"]  # 按发布日期倒序排序

    def __str__(self):
        return self.name
