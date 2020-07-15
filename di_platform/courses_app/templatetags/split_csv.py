from django import template

register = template.Library() 

@register.filter(name='split_csv') 
def split_csv(value, arg):
    return value.split(arg)