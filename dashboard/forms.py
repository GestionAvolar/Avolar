from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Profile, Entree, Sortie, EtatBesoin, ArticleBesoin, MaterielNonConsommable, 
    Projet, Offre, Justificatif, DetailJustificatif,
    TermeReference, RapportMission, Planification, Consultant, 
    Affectation, PresenceJournaliere, ElementProjet,
    FormulaireTerrain, ChampFormulaire, SoumissionDonnee
)

# --- Formulaires de Caisse ---
class EntreeForm(forms.ModelForm):
    class Meta:
        model = Entree
        fields = ['date', 'no_bon', 'provenance', 'montant_recu', 'motif', 'no_contrat']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'no_bon': forms.TextInput(attrs={'class': 'form-control'}),
            'provenance': forms.TextInput(attrs={'class': 'form-control'}),
            'montant_recu': forms.NumberInput(attrs={'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'no_contrat': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SortieForm(forms.ModelForm):
    class Meta:
        model = Sortie
        fields = ['no_bon', 'projet', 'nom_beneficiaire', 'fonction', 'montant_paye', 'motif', 'no_ordre_paiement']
        widgets = {
            'no_bon': forms.TextInput(attrs={'class': 'form-control'}),
            'projet': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_beneficiaire': forms.TextInput(attrs={'class': 'form-control'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'montant_paye': forms.NumberInput(attrs={'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'no_ordre_paiement': forms.TextInput(attrs={'class': 'form-control'}),
        }

# --- Logistique & Besoins ---
class EtatBesoinForm(forms.ModelForm):
    class Meta:
        model = EtatBesoin
        exclude = ['no_etat_besoin']
        widgets = {'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})}

ArticleFormSet = inlineformset_factory(
    EtatBesoin, ArticleBesoin, 
    fields=['designation', 'quantite', 'prix_unitaire', 'observation'],
    extra=5, can_delete=True
)

class MaterielForm(forms.ModelForm):
    class Meta:
        model = MaterielNonConsommable
        exclude = ['no_reference']

# --- Projets, Offres & Éléments ---
class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['nom', 'logo', 'bailleur_fond', 'no_contrat', 'cout_global', 'zone_intervention', 'date_debut', 'date_fin']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ['nom_projet', 'terme_reference', 'duree_mission', 'bailleur_fond', 'zone_intervention', 'document_proposition']

class ElementProjetForm(forms.ModelForm):
    class Meta:
        model = ElementProjet
        fields = ['titre', 'description', 'fichier', 'type_element']

# --- Justificatifs, S&E, RH ---
class JustificatifForm(forms.ModelForm):
    class Meta:
        model = Justificatif
        fields = ['etablissement', 'date', 'no_bon', 'piece_jointe']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

DetailJustificatifFormSet = inlineformset_factory(
    Justificatif, DetailJustificatif, 
    fields=['article', 'quantite', 'prix_unitaire'],
    extra=5, can_delete=True
)

class TDRForm(forms.ModelForm):
    class Meta:
        model = TermeReference
        fields = ['projet', 'date_debut', 'date_fin', 'zone_intervention', 'fichier']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class RapportMissionForm(forms.ModelForm):
    class Meta:
        model = RapportMission
        fields = ['tdr', 'projet', 'date_debut', 'date_fin', 'zone_intervention', 'fichier', 'observation_se']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class PlanificationForm(forms.ModelForm):
    class Meta:
        model = Planification
        fields = [
            'projet', 
            'mission_titre', 
            'activite_prevue', 
            'activite_realisee', 
            'date_debut', 
            'date_fin', 
            'zone_intervention'
        ]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class ConsultantForm(forms.ModelForm):
    class Meta:
        model = Consultant
        fields = ['nom_complet', 'profession_base', 'date_naissance', 'etudes_faites', 'cv', 'projet', 'fonction_occupee']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class AffectationForm(forms.ModelForm):
    class Meta:
        model = Affectation
        exclude = ['consultant']

class PresenceForm(forms.ModelForm):
    class Meta:
        model = PresenceJournaliere
        fields = ['consultant', 'heure_arrivee', 'heure_depart', 'statut', 'remarques']
        widgets = {
            'heure_arrivee': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_depart': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'remarques': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# --- Utilisateurs & Profils ---
class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('Logisticien', 'Logisticien'),
        ('Suivi et Evaluation', 'Suivi et Evaluation'),
        ('Ressources Humaines', 'Ressources Humaines'),
        ('Coordonnateur national', 'Coordonnateur national'),
        ('Assistant Financier', 'Assistant Financier'),
        ('Offres et Service', 'Offres et Service'),
        ('Chef de projet', 'Chef de projet'),
        ('Agro animateur', 'Agro animateur'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        label="Rôle / Groupe",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['projet', 'role']

# --- Formulaires de Terrain & Collecte ---
from django import forms
from .models import FormulaireTerrain, ChampFormulaire

class FormulaireTerrainForm(forms.ModelForm):
    class Meta:
        model = FormulaireTerrain
        fields = ['titre', 'description', 'projet']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'projet': forms.Select(attrs={'class': 'form-select'}),
        }

class ChampFormulaireForm(forms.ModelForm):
    class Meta:
        model = ChampFormulaire
        fields = ['libelle_question', 'type_champ', 'options', 'est_obligatoire', 'ordre']
        widgets = {
            'libelle_question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Quel est le statut de la parcelle ?'}),
            'type_champ': forms.Select(attrs={'class': 'form-select', 'id': 'id_type_champ'}),
            # On utilise un Textarea pour que l'utilisateur puisse entrer plusieurs options confortablement
            'options': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Ex: Option 1, Option 2, Option 3 (Requis uniquement pour choix unique/multiple)'
            }),
            'est_obligatoire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordre': forms.NumberInput(attrs={'class': 'form-control'}),
        }