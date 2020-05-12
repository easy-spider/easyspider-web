from django import template

register = template.Library()
CARD_EACH_ROW = 4


@register.filter
def remainder_list(value):
    return range(0, CARD_EACH_ROW - value % CARD_EACH_ROW)


@register.filter
def get_dict_value(my_dict, key):
    """获取dict中的值"""
    return my_dict[key]
