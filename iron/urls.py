from rest_framework import routers

from iron.api import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('files', views.File, 'file')

urlpatterns = router.urls
