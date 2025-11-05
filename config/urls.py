# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
	path('', include('speedy_app.core.urls', namespace='core')),
	# Reporting panel with separate login/dashboard
	path('reports/', include('reports.urls', namespace='reports')),
	# Chat system URLs
	path('chat/', include('chat.urls', namespace='chat')),
	# Serve a minimal inline SVG as a favicon so browsers don't hit a 404 for /favicon.ico
	path('favicon.ico', lambda request: HttpResponse(
		'<?xml version="1.0" encoding="utf-8"?>\n'
		'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">\n'
		'  <rect width="100%" height="100%" fill="#007bff"/>\n'
		'  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"\n'
		'        font-family="Arial, Helvetica, sans-serif" font-size="34" fill="#fff">S</text>\n'
		'</svg>', content_type='image/svg+xml')),
]

# Serve static and media files during development
if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_URL) # Corrected MEDIA_URL here
