from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('login/', views.connexion, name='connexion'),
    path('logout/', views.deconnexion, name='deconnexion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profil/', views.profil, name='profil'),

    # Clubs
    path('clubs/', views.liste_clubs, name='liste_clubs'),
    path('clubs/creer/', views.creer_club, name='creer_club'),
    path('clubs/<int:pk>/', views.detail_club, name='detail_club'),
    path('clubs/<int:pk>/modifier/', views.modifier_club, name='modifier_club'),
    path('clubs/<int:pk>/supprimer/', views.supprimer_club, name='supprimer_club'),

    # Adhésions
    path('clubs/<int:club_pk>/adherer/', views.demander_adhesion, name='demander_adhesion'),
    path('clubs/<int:club_pk>/adhesions/', views.gerer_adhesions, name='gerer_adhesions'),
    path('adhesions/<int:pk>/<str:action>/', views.traiter_adhesion, name='traiter_adhesion'),

    # Événements
    path('evenements/', views.liste_evenements, name='liste_evenements'),
    path('clubs/<int:club_pk>/evenements/creer/', views.creer_evenement, name='creer_evenement'),
    path('evenements/<int:pk>/inscrire/', views.inscrire_evenement, name='inscrire_evenement'),
    path('participations/<int:pk>/annuler/', views.annuler_participation, name='annuler_participation'),

    # Admin
    path('admin-panel/utilisateurs/', views.gerer_utilisateurs, name='gerer_utilisateurs'),
    path('admin-panel/utilisateurs/<int:user_pk>/role/<str:role>/', views.changer_role, name='changer_role'),
    path('admin-panel/statistiques/', views.statistiques, name='statistiques'),
]
