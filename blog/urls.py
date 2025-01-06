from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('posts', views.PostViewSet, basename='posts')

urlpatterns = router.urls