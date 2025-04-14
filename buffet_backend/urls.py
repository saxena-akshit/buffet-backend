from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the URLs from the financials_api app
    path('api/', include('financials_api.urls')),
    # Add other project-level URLs here if needed
]
