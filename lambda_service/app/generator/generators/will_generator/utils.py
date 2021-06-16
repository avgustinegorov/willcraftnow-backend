from ..mark_safe import mark_safe
from collections import OrderedDict
from ..base_utils import BaseUtils


class Utils(BaseUtils):

    def SubParagraphBullet(self, index):
        return mark_safe(
            f"<bullet bulletAnchor='start' bulletFontSize='12'>{self.roman(index+1)}.</bullet>"
        )

    def ParagraphBullet(self):
        return mark_safe(
            f"<bullet bulletAnchor='start' bulletFontSize='12'><seq id='bulletCount'"
            f" />.</bullet>"
        )

    def SubParagraphWrapper(self, value, count, context):
        spaceBefore = context["spaceBefore"]
        subLeftIndent = context["subLeftIndent"]
        subBulletLeftIndent = context["subBulletLeftIndent"]

        result = (
            f"<para fontSize='12' leftIndent='{subLeftIndent}' spaceBefore='{spaceBefore}'"
            f" bulletIndent='{subBulletLeftIndent}'> {self.SubParagraphBullet(count)} {value}"
            " </para>"
        )
        return mark_safe(result)

    def ParagraphWrapper(self, value, context, count):
        reset = "<seqreset id='bulletCount' />" if count == 0 else ""
        spaceBefore = context["spaceBefore"]
        LeftIndent = context["LeftIndent"]
        result = (
            f"<para fontSize='12' leftIndent='{LeftIndent}' spaceBefore='{spaceBefore}'>"
            f" {reset}{self.ParagraphBullet()} {value} </para>"
        )
        return mark_safe(result)

    def ParagraphWrapperNoBullet(self, value, context):
        spaceBefore = context["spaceBefore"]
        LeftIndent = context["LeftIndent"]
        result = (
            f"<para fontSize='12' leftIndent='{LeftIndent}' spaceBefore='{spaceBefore}'>"
            f" {value} </para>"
        )
        return mark_safe(result)

    def AssetHeaderWrapper(self, value, context):
        spaceBefore = context["spaceBefore"]
        return mark_safe(
            f"<para fontSize='12' spaceBefore='{spaceBefore}'><b>{value}</b></para>"
        )
