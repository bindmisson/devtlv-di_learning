from django.shortcuts import render, redirect


def intro_html_css(request):
    return render(request, 'intro_html_css.html')


def intro_fullstack_js(request):
    return render(request, 'intro_fullstack_js.html')


def intro_fullstack_python(request):
    return render(request, 'intro_fullstack_python.html')


def dashboard(request):
    # NEED TO EDIT TEMPLATE (grey background color not showing up)
    return render(request, 'dashboard.html')


def apply(request):
    return render(request, 'apply.html')


def pricing(request):
    # NEED TO EDIT TEMPLATE (grey background color not showing up)
    return render(request, 'pricing.html')


def terms(request):
    # NEED TO EDIT TEMPLATE (fix navbar to prospect navbar design)
    return render(request, 'prospect_terms.html')


def privacy(request):
    # NEED TO EDIT TEMPLATE (fix navbar to prospect navbar design)
    return render(request, 'prospect_privacy.html')