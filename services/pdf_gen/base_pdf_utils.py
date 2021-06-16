from collections import OrderedDict

from django.utils.safestring import mark_safe


def roman(num):
    """ Converts a Number to a roman numeral """
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= r * x
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)]).lower()


def SubParagraphBullet(index):
    return mark_safe(
        f"<bullet bulletAnchor='start' bulletFontSize='12'>{roman(index+1)}.</bullet>"
    )


def ParagraphBullet():
    return mark_safe(
        f"<bullet bulletAnchor='start' bulletFontSize='12'><seq id='bulletCount'"
        f" />.</bullet>"
    )


def SubParagraphWrapper(value, count, context):
    spaceBefore = context["spaceBefore"]
    subLeftIndent = context["subLeftIndent"]
    subBulletLeftIndent = context["subBulletLeftIndent"]

    result = (
        f"<para fontSize='12' leftIndent='{subLeftIndent}' spaceBefore='{spaceBefore}'"
        f" bulletIndent='{subBulletLeftIndent}'> {SubParagraphBullet(count)} {value}"
        " </para>"
    )
    return mark_safe(result)


def ParagraphWrapper(value, context, count):
    reset = "<seqreset id='bulletCount' />" if count == 0 else ""
    spaceBefore = context["spaceBefore"]
    LeftIndent = context["LeftIndent"]
    result = (
        f"<para fontSize='12' leftIndent='{LeftIndent}' spaceBefore='{spaceBefore}'>"
        f" {reset}{ParagraphBullet()} {value} </para>"
    )
    return mark_safe(result)


def ParagraphWrapperNoBullet(value, context):
    spaceBefore = context["spaceBefore"]
    LeftIndent = context["LeftIndent"]
    result = (
        f"<para fontSize='12' leftIndent='{LeftIndent}' spaceBefore='{spaceBefore}'>"
        f" {value} </para>"
    )
    return mark_safe(result)


def AssetHeaderWrapper(value, context):
    spaceBefore = context["spaceBefore"]
    return mark_safe(
        f"<para fontSize='12' spaceBefore='{spaceBefore}'><b>{value}</b></para>"
    )
