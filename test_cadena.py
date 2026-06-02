import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eje_central_back.settings")
django.setup()

from django.test import RequestFactory
from plantilla.views import CadenaMandoView

factory = RequestFactory()
request = factory.get('/plantilla/cadena_mando/?q=10347180')
view = CadenaMandoView.as_view()
response = view(request)
print(response.status_code)
print(response.data)
