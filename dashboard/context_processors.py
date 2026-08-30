def user_permissions(request):
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    is_super = user.is_superuser
    groups = [g.name.lower() for g in user.groups.all()]
    
    is_coord = "coordonnateur national" in groups or "coordinateur national" in groups
    is_agro = "agro animateur" in groups or "agro-animateur" in groups
    
    return {
        'can_see_finance': is_super or is_coord or "assistant financier" in groups or "finance" in groups,
        'can_see_logistics': is_super or is_coord or "logisticien" in groups or "logistique" in groups,
        'can_see_projects': is_super or is_coord or "chef de projet" in groups or "projets" in groups,
        'can_see_terrain': is_super or is_coord or is_agro,
        'can_see_se': is_super or is_coord or "suivi et évaluation" in groups or "suivi & évaluation" in groups,
        'can_see_offres': is_super or is_coord or "offre et service" in groups or "offres et service" in groups,
    }