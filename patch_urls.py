import re

with open('/home/edgar/ANAM/EjeCentral/eje_central_back/plantilla/urls.py', 'r') as f:
    content = f.read()

content = content.replace(
    'path(\n        "torre-caballito/empleados/",\n        TorreCaballitoEmpleadosView.as_view(),\n        name="torre-caballito-empleados",\n    ),',
    'path(\n        "torre-caballito/empleados/",\n        TorreCaballitoEmpleadosView.as_view(),\n        name="torre-caballito-empleados",\n    ),\n    path(\n        "torre-caballito/search/",\n        TorreCaballitoSearchView.as_view(),\n        name="torre-caballito-search",\n    ),'
)

with open('/home/edgar/ANAM/EjeCentral/eje_central_back/plantilla/urls.py', 'w') as f:
    f.write(content)
