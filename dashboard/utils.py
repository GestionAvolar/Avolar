from django.core.exceptions import PermissionDenied

def verifier_acces_projet(user, projet_id):
    """Vérifie si l'utilisateur a le droit d'agir sur ce projet."""
    if user.groups.filter(name='Coordonnateur').exists():
        return True
    if hasattr(user, 'projet') and user.projet.id == projet_id:
        return True
    return False

def restreindre_modification(view_func):
    """Empêche Finance/Logistique de modifier/supprimer."""
    def wrap(request, *args, **kwargs):
        if request.user.groups.filter(name__in=['Coordonnateur', 'Chef de Projet']).exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Vous n'avez pas le droit de modifier cette donnée.")
    return wrap