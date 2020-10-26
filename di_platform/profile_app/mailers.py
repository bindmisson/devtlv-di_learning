from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.conf import settings
from mailjet_rest import Client


def reset_password_email(request, user):
  mailjet = Client(
    auth=(settings.MJ_APIKEY_PUBLIC, settings.MJ_APIKEY_PRIVATE),
    version='v3.1',
    api_url='https://api.mailjet.com/'
  )

  current_site = get_current_site(request)
  data = {
    'Messages': [
      {
        "From": {
          "Email": settings.MJ_SENDER_EMAIL,
          "Name": "Developers Institute Contact"
        },
        "To": [
          {
            "Email": user.email,
            "Name": user.username
          }
        ],
        "TemplateID": 1809263,
        "TemplateLanguage": True,
        "Subject": "Developers Institute Password Reset",
        "Variables": {
          "first_name": user.username,
          "pW_reset_link": render_to_string('password_link.html', {
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
          })
        }

      }
    ]
  }

  a = mailjet.send.create(data=data)
  print(a)

