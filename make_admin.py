import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Mets ici ton nom d'utilisateur exact et le mot de passe que tu veux utiliser pour te connecter
username = "admin"  # Remplace par ton pseudo si c'est différent
email = "admin@example.com"
password = "MonSuperPassword123"  # Ton mot de passe

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"SUCCÈS : Le compte '{username}' a été créé en tant que superutilisateur !")
else:
    user = User.objects.get(username=username)
    user.is_superuser = True
    user.is_staff = True
    user.set_password(password)
    user.save()
    print(f"SUCCÈS : Le compte '{username}' a reçu tous les droits administrateurs !")