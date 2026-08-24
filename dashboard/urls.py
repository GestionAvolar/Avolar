from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth.views import LogoutView
urlpatterns = [ 
    # Accueil et Finance
    path('finance/', views.finance_view, name='finance_view'),
    path('finance/choix/', views.finance_choix, name='finance_choix'),
    
    # Journal & Caisse
    path('entree/ajouter/', views.ajouter_entree, name='ajouter_entree'),
    path('sortie/ajouter/', views.ajouter_sortie, name='ajouter_sortie'),
    path('journal/', views.journal_caisse, name='journal_caisse'),
    
    # Logistique
    path('logistique/', views.logistique_home, name='logistique_home'),
    path('besoin/creer/', views.creer_etat_besoin, name='creer_etat_besoin'),
    path('besoins/', views.liste_etats_besoin, name='liste_etats_besoin'),
    path('materiel/ajouter/', views.ajouter_materiel, name='ajouter_materiel'),
    path('materiels/', views.liste_materiels, name='liste_materiels'),
    
    # Projets & Offres
    path('projet/ajouter/', views.ajouter_projet, name='ajouter_projet'),
    path('projets/', views.liste_projets, name='liste_projets'),
    # LIGNE AJOUTÉE CI-DESSOUS POUR CORRIGER L'ERREUR NoReverseMatch
    path('projet/<int:id>/', views.detail_projet, name='detail_projet'),
    path('offre/ajouter/', views.ajouter_offre, name='ajouter_offre'),
    path('offres/', views.liste_offres, name='liste_offres'),
    
    # Justificatifs
    path('justificatif/ajouter/', views.ajouter_justificatif, name='ajouter_justificatif'),
    
    # Suivi & Évaluation
    path('se/', views.se_home, name='se_home'),
    path('tdr/ajouter/', views.ajouter_tdr, name='ajouter_tdr'),
    path('tdrs/', views.liste_tdr, name='liste_tdr'),
    path('rapport/ajouter/', views.ajouter_rapport, name='ajouter_rapport'),
    path('rapports/', views.liste_rapports, name='liste_rapports'),
    path('planification/ajouter/', views.ajouter_planification, name='ajouter_planification'),
    path('planifications/', views.liste_planifications, name='liste_planifications'),
    
    # Ressources Humaines (RH)
    path('rh/consultants/', views.liste_consultants, name='liste_consultants'),
    path('rh/consultant/<int:id>/', views.voir_consultant, name='voir_consultant'),
    path('rh/consultant/ajouter/', views.ajouter_consultant, name='ajouter_consultant'),
    path('rh/consultant/affecter/<int:id>/', views.affecter_consultant, name='affecter_consultant'),
    path('rh/consultant/modifier/<int:id>/', views.modifier_consultant, name='modifier_consultant'),
    path('rh/consultant/supprimer/<int:id>/', views.supprimer_consultant, name='supprimer_consultant'),
    path('rh/presence/', views.presence_rh, name='presence_rh'),
    
    # Gestion des utilisateurs et Déconnexion
    path('home/', views.home, name='home'),
    path('creer-utilisateur/', views.creer_utilisateur, name='creer_utilisateur'),
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('besoin/<int:id>/', views.visualiser_besoin, name='visualiser_besoin'),
    path('besoin/modifier/<int:id>/', views.modifier_besoin, name='modifier_besoin'),
    path('besoin/supprimer/<int:id>/', views.supprimer_besoin, name='supprimer_besoin'),
    path('besoin/exporter/<str:format>/<int:id>/', views.exporter_besoin, name='exporter_besoin'),
    path('materiel/modifier/<int:id>/', views.modifier_materiel, name='modifier_materiel'),
    path('materiel/supprimer/<int:id>/', views.supprimer_materiel, name='supprimer_materiel'),
    path('projet/<int:projet_id>/ajouter-element/', views.ajouter_element, name='ajouter_element'),
    path('element/modifier/<int:id>/', views.modifier_element, name='modifier_element'),
    path('element/supprimer/<int:id>/', views.supprimer_element, name='supprimer_element'),
    path('projet/modifier/<int:id>/', views.modifier_projet, name='modifier_projet'),
    path('projet/supprimer/<int:id>/', views.supprimer_projet, name='supprimer_projet'),
    path('transaction/supprimer/<int:id>/', views.supprimer_transaction, name='supprimer_transaction'),
    path('transaction/modifier/<int:id>/', views.modifier_transaction, name='modifier_transaction'),
    path('journal/export/excel/', views.exporter_journal_excel, name='exporter_journal_excel'),
    path('utilisateur/modifier/<int:id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateur/supprimer/<int:id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    # Page de connexion à la racine
    path('', CustomLoginView.as_view(), name='login'),
    # Autres paths...
    path('logout/', LogoutView.as_view(), name='logout'),
    # ... vos autres URLs existantes ...
    path('terrain/formulaires/', views.liste_formulaires_terrain, name='liste_formulaires_terrain'),
    path('terrain/formulaires/creer/', views.creer_formulaire_terrain, name='creer_formulaire_terrain'),
    path('terrain/formulaires/<int:pk>/remplir/', views.remplir_formulaire_terrain, name='remplir_formulaire_terrain'),
    path('formulaires/supprimer/<int:pk>/', views.supprimer_formulaire_terrain, name='supprimer_formulaire_terrain'),
    path('soumissions/centralisees/', views.liste_toutes_soumissions, name='liste_toutes_soumissions'),
    path('soumission/<int:pk>/', views.detail_soumission, name='detail_soumission'),
    path('terrain/formulaires/<int:pk>/modifier/', views.modifier_formulaire_terrain, name='modifier_formulaire_terrain'),
]