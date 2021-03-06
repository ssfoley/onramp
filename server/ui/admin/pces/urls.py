from django.conf.urls import url
import views

urlpatterns = [
    url(r'GetAll/$', views.get_all_pces),
    url(r'Modules/$', views.get_pce_modules),
    url(r'Module/Add/$', views.add_pce_module),
    url(r'Module/Edit/$', views.edit_pce_module),
    url(r'Module/Delete/$', views.delete_pce_module),
    url(r'Module/State/$', views.get_module_state),
    url(r'Module/Deploy/$', views.deploy_module),
    url(r'Add/$', views.add_pce),
    url(r'Edit/$', views.edit_pce),
    url(r'Delete/$', views.delete_pce),
    url(r'Workspaces/$', views.get_pce_workspaces),
    url(r'Jobs/$', views.get_pce_jobs),
    url(r'^$', views.main),
]
