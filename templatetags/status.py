from django import template
register = template.Library()

def status(value): #check Condition here

    if value ==True:
        return "<span class='label label-success'>approuve</span>"
    elif value ==False :
        return "<span class='label label-warning'>attente</span>"
    else:
        return "<span class='label label-danger'>ferme</span>"

register.filter('status',status)