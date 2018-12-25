from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from api import views

urlpatterns = [
    path('getAcConfigs/', views.AcConfigList.as_view()),
    path('auth/', views.Auth.as_view()),
    path('logout/', views.Logout.as_view()),
    path('changePassword/', views.ChangePassword.as_view()),
    path('setPassword/', views.SetPassword.as_view()),
    path('setPreference/', views.SetPreference.as_view()),
    path('updateAcConfig/', views.UpdateAcConfig.as_view()),
    path('getCurrentAcConfig/', views.GetCurrentAcConfig.as_view()),
    path('getPreference/', views.GetPreference.as_view()),
    path('getSleepTimes/', views.GetSleepTimes.as_view()),
    path('addSleepTime/', views.AddSleepTime.as_view()),
    path('deleteSleepTime/', views.DeleteSleepTime.as_view()),
    path('getBootTimes/', views.GetBootTimes.as_view()),
    path('addBootTime/', views.AddBootTime.as_view()),
    path('deleteBootTime/', views.DeleteBootTime.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
