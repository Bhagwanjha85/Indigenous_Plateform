from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path("accounts/", include("accounts.urls")),
    path("blogs/", include("blogs.urls")),
    path("manage/", include("management.urls")),

    path("", views.Index.as_view(), name="index"),
    path("about/", views.about.as_view(), name="about"),
    path("blog/", views.blog.as_view(), name="blog"),
    path("search/", views.Search.as_view(), name="search"),
    path("bookmark/", views.BookmarkView.as_view(), name="bookmark"),
    path("terms-and-conditions/", views.TermsAndConditions.as_view(), name="terms_and_conditions"),
    path("category/", views.CategoryView.as_view(), name="category"),
    path("category/<slug:cat>/", views.GetCategory.as_view(), name="get_category"),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
