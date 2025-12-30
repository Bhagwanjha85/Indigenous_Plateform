from django.conf import settings
from blogs.models import SiteView

def admin_media(request):
    return settings.GLOBAL_SETTINGS

def visitor_count(request):  # Name change kiya
    """Add visitor count to all templates - increment on every page load"""
    
    site_view, created = SiteView.objects.get_or_create(id=1)
    
    # Increment count on EVERY page load (including refresh)
    site_view.total_views += 1
    site_view.save()
    
    return {
        "site_views": site_view.total_views
    }