from django.conf.urls import url
from main import views
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    url(r'^api/token/$',jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^serve/faq/child/pages/$', views.serve_faq_child_pages),
    url(r'^serve/advisory/child/pages/$', views.serve_advisory_child_page),
    url(r'^serve/url/for/pdf/and/video/$', views.serve_url_for_pdf_and_video),
    url(r'^serve/terms/and/conditions/pages/$', views.serve_terms_and_conditions_egavel),
    url(r'^save/terms/and/conditions/pages/$', views.save_terms_and_conditions_egavel),
    url(r'^serve/raq/details/$', views.serve_raq_details),
    url(r'^serve/featured/video/link/$', views.serve_featured_video_link),
    url(r'^serve/products/list/$', views.serve_products_list),
    url(r'^serve/publication/$', views.serve_publication),
]