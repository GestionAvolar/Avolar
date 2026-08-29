import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Mets ici ton NOM D'UTILISATEUR exact (celui avec lequel tu te connectes)
username = "admin"  # <--- Change ici si ton pseudo est différent
email = "admin@example.com"
password = "TonMotDePasseSecret123"  # <--- Ton mot de passe

# 1. Création ou récupération du compte en mode Superutilisateur total
if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    print(f"Création du compte superutilisateur '{username}'...")
else:
    user = User.objects.get(username=username)
    user.is_superuser = True
    user.is_staff = True
    user.set_password(password)
    user.save()
    print(f"Mise à jour des privilèges superuser pour '{username}'...")

# 2. Attribution du profil 'Coordonnateur national' (pour tout voir)
if hasattr(user, 'profile'):
    user.profile.role = 'Coordonnateur national'
    user.profile.projet = None  # Accès à tous les projets
    user.profile.save()
    print("Profil mis à jour : Rôle 'Coordonnateur national' assigné.")

# 3. S'assurer qu'il n'est PAS dans le groupe restreint 'Agro animateur'
for group_name in ['Agro animateur', 'Logisticien', 'Assistant Financier']:
    group = Group.objects.filter(name=group_name).first()
    if group and user.groups.filter(name=group_name).exists():
        user.groups.remove(group)
        print(f"Retrait du groupe restreint '{group_name}'.")

print("Configuration administrateur appliquée avec succès !")