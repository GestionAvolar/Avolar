from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

import datetime

# --- LOGISTIQUE & FINANCE ---
class Entree(models.Model):
    no_bon = models.CharField(max_length=50, verbose_name="Numéro de Bon")
    provenance = models.CharField(max_length=200)
    montant_recu = models.DecimalField(max_digits=12, decimal_places=2)
    motif = models.TextField()
    no_contrat = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(default=timezone.now) 

    def __str__(self):
        return f"{self.no_bon} - {self.provenance}"

class Sortie(models.Model):
    no_bon = models.CharField(max_length=50, verbose_name="Numéro de Bon")
    projet = models.CharField(max_length=200)
    nom_beneficiaire = models.CharField(max_length=200)
    fonction = models.CharField(max_length=100)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2)
    motif = models.TextField()
    no_ordre_paiement = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    def __str__(self): return f"{self.no_bon} - {self.nom_beneficiaire}"

class EtatBesoin(models.Model):
    no_etat_besoin = models.CharField(max_length=50, unique=True, verbose_name="N° État de besoin", blank=True)
    date = models.DateField(default=timezone.now)
    projet_demandeur = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    valide = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.no_etat_besoin:
            year = timezone.now().year
            count = EtatBesoin.objects.filter(date__year=year).count() + 1
            self.no_etat_besoin = f"EB-{year}-{count:03d}"
        super().save(*args, **kwargs)
    def __str__(self): return self.no_etat_besoin

class ArticleBesoin(models.Model):
    etat_besoin = models.ForeignKey(EtatBesoin, related_name='articles', on_delete=models.CASCADE)
    designation = models.CharField(max_length=255)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    observation = models.TextField(blank=True)
    def __str__(self): return self.designation

# --- PROJETS & GESTION ---
class Projet(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom du Projet")
    logo = models.ImageField(upload_to='projets/logos/', null=True, blank=True, verbose_name="Logo du Projet")
    bailleur_fond = models.CharField(max_length=200, verbose_name="Bailleur de Fonds")
    no_contrat = models.CharField(max_length=100, verbose_name="N° Contrat Projet & Avolar")
    cout_global = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Coût Global")
    zone_intervention = models.CharField(max_length=255, verbose_name="Zone d'intervention")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    chef_projet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nom

class PhotoProjet(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='projets/photos/')

class RapportProjet(models.Model):
    TYPE_RAPPORT = [('Livrable', 'Livrable'), ('Mission', 'Mission'), ('Mensuel', 'Mensuel'), ('Trimestriel', 'Trimestriel'), ('Final', 'Final')]
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='rapports')
    type = models.CharField(max_length=20, choices=TYPE_RAPPORT)
    fichier = models.FileField(upload_to='projets/rapports/')
    date_upload = models.DateTimeField(auto_now_add=True)

class MaterielNonConsommable(models.Model):
    designation = models.CharField(max_length=200)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='materiels')
    no_reference = models.CharField(max_length=100, unique=True, blank=True)
    etat = models.CharField(max_length=50, choices=[('Neuf', 'Neuf'), ('Bon', 'Bon'), ('Usagé', 'Usagé')])
    date_achat = models.DateField()
    imputation = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        if not self.no_reference:
            prefixe = self.designation[:4].upper()
            nom_projet = self.projet.nom.upper().replace(" ", "-")
            count = MaterielNonConsommable.objects.filter(projet=self.projet).count() + 1
            self.no_reference = f"{prefixe}-{nom_projet}-AVOLAR-{count:03d}"
        super().save(*args, **kwargs)
    def __str__(self): return self.no_reference

# --- RESSOURCES HUMAINES ---
class Consultant(models.Model):
    nom_complet = models.CharField(max_length=200)
    profession_base = models.CharField(max_length=150)
    date_naissance = models.DateField()
    etudes_faites = models.TextField()
    cv = models.FileField(upload_to='cv_consultants/')
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultants')
    fonction_occupee = models.CharField(max_length=150, blank=True, null=True)
    def __str__(self): return self.nom_complet

class Affectation(models.Model):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    fonction = models.CharField(max_length=100)
    site = models.CharField(max_length=100)
    salaire = models.DecimalField(max_digits=10, decimal_places=2)
    taches_principales = models.TextField()

class PresenceJournaliere(models.Model):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=[('Présent', 'Présent'), ('Absent', 'Absent'), ('Congé', 'Congé')])
    remarques = models.TextField(blank=True, null=True)
    class Meta: ordering = ['-date']

# --- S&E, OFFRES & JUSTIFICATIFS ---
class Offre(models.Model):
    nom_projet = models.CharField(max_length=200)
    terme_reference = models.FileField(upload_to='tdr/')
    duree_mission = models.CharField(max_length=100)
    bailleur_fond = models.CharField(max_length=200)
    zone_intervention = models.CharField(max_length=255)
    document_proposition = models.FileField(upload_to='propositions/', null=True, blank=True)
    est_soumise = models.BooleanField(default=False)
    est_validee = models.BooleanField(default=False)

class Justificatif(models.Model):
    etablissement = models.CharField(max_length=200)
    date = models.DateField()
    no_bon = models.CharField(max_length=50, unique=True)
    piece_jointe = models.FileField(upload_to='justificatifs/')
    def __str__(self): return self.no_bon

class DetailJustificatif(models.Model):
    justificatif = models.ForeignKey(Justificatif, on_delete=models.CASCADE, related_name='articles')
    article = models.CharField(max_length=200)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

class TermeReference(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='tdrs')
    date_debut = models.DateField()
    date_fin = models.DateField()
    zone_intervention = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='tdr/')

class RapportMission(models.Model):
    tdr = models.ForeignKey(TermeReference, on_delete=models.CASCADE, related_name='rapports')
    projet = models.CharField(max_length=200)
    date_debut = models.DateField()
    date_fin = models.DateField()
    zone_intervention = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='rapports/')
    observation_se = models.TextField(verbose_name="Observation Responsable S&E", blank=True)

class Planification(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='planifications', verbose_name="Projet concerné")
    mission_titre = models.CharField(max_length=200, verbose_name="Titre de la mission")
    activite_prevue = models.TextField(verbose_name="Activité prévues")
    activite_realisee = models.TextField(blank=True, null=True, verbose_name="Activités réalisées")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    zone_intervention = models.CharField(max_length=255, verbose_name="Zone d'intervention")
    def __str__(self):
        return f"{self.mission_titre} - {self.projet}"

class ElementProjet(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='elements')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='projets/documents/', blank=True, null=True)
    type_element = models.CharField(max_length=50, choices=[('RAPPORT', 'Rapport'), ('LIVRABLE', 'Livrable'), ('AUTRE', 'Autre')])
    date_ajout = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.titre} - {self.projet.nom}"

class MouvementFinance(models.Model):
    TYPE_CHOICES = (('ENTREE', 'Entrée'), ('SORTIE', 'Sortie'))
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, null=True, blank=True)
    justificatif = models.FileField(upload_to='justificatifs/', blank=True, null=True)
    numero_piece = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    provenance_beneficiaire = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self): return f"{self.type} - {self.montant}$"

# --- PROFIL UTILISATEUR & SIGNAUX ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=50, blank=True)
    def __str__(self): return f"Profil de {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

def get_donnees_par_projet(user):
    if user.groups.filter(name='Coordonnateur national').exists() or user.is_superuser:
        return MouvementFinance.objects.all()
    return MouvementFinance.objects.filter(projet=user.profile.projet)

# --- FORMULAIRES DE TERRAIN ---
class FormulaireTerrain(models.Model):
    titre = models.CharField(max_length=255, verbose_name="Titre du formulaire")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name="formulaires", verbose_name="Projet associé")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class ChampFormulaire(models.Model):
    TYPES_CHAMPS = [
        ('texte', 'Texte court'),
        ('texte_long', 'Texte long (Paragraphe)'),
        ('nombre', 'Chiffre / Nombre'),
        ('date', 'Date'),
        ('heure', 'Heure'),
        ('choix_unique', 'Sélection / Choix unique'),
        ('choix_multiple', 'Cases à cocher (Choix multiple)'),
        ('gps', 'Coordonnées GPS (Géolocalisation)'),
        ('photo', 'Photo (Appareil ou Importation)'),
        ('signature', 'Signature numérique'),
    ]

    formulaire = models.ForeignKey(FormulaireTerrain, on_delete=models.CASCADE, related_name="champs")
    libelle_question = models.CharField(max_length=255, verbose_name="Question / Intitulé du champ")
    type_champ = models.CharField(max_length=50, choices=TYPES_CHAMPS, verbose_name="Type de réponse")
    options = models.TextField(blank=True, null=True, help_text="Séparez les options par une virgule.")
    est_obligatoire = models.BooleanField(default=True, verbose_name="Champ obligatoire")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    def __str__(self):
        return f"{self.libelle_question} ({self.get_type_champ_display()})"

class SoumissionDonnee(models.Model):
    formulaire = models.ForeignKey(FormulaireTerrain, on_delete=models.CASCADE, related_name='soumissions')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    donnees_json = models.JSONField() # Stocke les paires { "Question": "Réponse" }

    def __str__(self):
        return f"Soumission de {self.agent} pour {self.formulaire.titre} le {self.date_soumission.strftime('%d/%m/%Y')}"