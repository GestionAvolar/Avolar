from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db.models import Sum
from django.http import HttpResponse
import pandas as pd
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Profile, FormulaireTerrain, ChampFormulaire, SoumissionDonnee
from .models import (
    Entree, Sortie, EtatBesoin, MaterielNonConsommable, Projet, 
    Offre, Justificatif, TermeReference, RapportMission, Planification,
    Consultant, Affectation, PresenceJournaliere, MouvementFinance, ElementProjet
)
from .forms import (
    EntreeForm, SortieForm, EtatBesoinForm, ArticleFormSet, MaterielForm, 
    ProjetForm, OffreForm, JustificatifForm, DetailJustificatifFormSet,
    TDRForm, RapportMissionForm, PlanificationForm, ConsultantForm,
    AffectationForm, PresenceForm, ProfileForm, ElementProjetForm, CustomUserCreationForm,
    FormulaireTerrainForm, ChampFormulaireForm
)
from django.forms import inlineformset_factory

# --- Utilitaires ---
def paginate(request, queryset, count=20):
    paginator = Paginator(queryset, count)
    return paginator.get_page(request.GET.get('page'))

# --- Accueil & Finance ---
@login_required
def home(request):
    if not request.user.is_superuser and request.user.groups.filter(name='Agro animateur').exists():
        return redirect('liste_formulaires_terrain')
    return render(request, 'dashboard/home.html')

@login_required
def finance_view(request): return render(request, 'dashboard/finance.html')

@login_required
def finance_choix(request): return render(request, 'dashboard/finance_choix.html')

# --- Journal & Caisse ---
@login_required
def ajouter_entree(request):
    if request.method == 'POST':
        form = EntreeForm(request.POST, request.FILES)
        if form.is_valid():
            entree = form.save()
            MouvementFinance.objects.create(date=entree.date, provenance_beneficiaire=entree.provenance, 
                description=entree.motif or "Entrée", montant=entree.montant_recu or 0, numero_piece=entree.no_bon, type='ENTREE')
            return redirect('journal_caisse')
    return render(request, 'dashboard/ajouter_entree.html', {'form': EntreeForm()})

@login_required
def ajouter_sortie(request):
    if request.method == 'POST':
        form = SortieForm(request.POST, request.FILES)
        if form.is_valid():
            sortie = form.save()
            MouvementFinance.objects.create(date=sortie.date, provenance_beneficiaire=form.cleaned_data.get('nom_beneficiaire'),
                description=form.cleaned_data.get('motif'), montant=form.cleaned_data.get('montant_paye'), 
                numero_piece=form.cleaned_data.get('no_ordre_paiement'), type='SORTIE')
            return redirect('journal_caisse')
    return render(request, 'dashboard/ajouter_sortie.html', {'form': SortieForm()})

@login_required
def journal_caisse(request):
    mouvements = MouvementFinance.objects.all().order_by('date')
    total_entrees = MouvementFinance.objects.filter(type='ENTREE').aggregate(Sum('montant'))['montant__sum'] or 0
    total_sorties = MouvementFinance.objects.filter(type='SORTIE').aggregate(Sum('montant'))['montant__sum'] or 0
    return render(request, 'dashboard/journal.html', {'journal': mouvements, 'total_entrees': total_entrees, 
                  'total_sorties': total_sorties, 'solde_final': total_entrees - total_sorties})

@login_required
def modifier_transaction(request, id):
    mouvement = get_object_or_404(MouvementFinance, id=id)
    form = EntreeForm(request.POST or None, instance=mouvement) if mouvement.type == 'ENTREE' else SortieForm(request.POST or None, instance=mouvement)
    if form.is_valid():
        form.save()
        return redirect('journal_caisse')
    return render(request, 'dashboard/modifier_transaction.html', {'form': form, 'mouvement': mouvement})

@login_required
def supprimer_transaction(request, id):
    mouvement = get_object_or_404(MouvementFinance, id=id)
    if request.method == 'POST':
        mouvement.delete()
        return redirect('journal_caisse')
    return render(request, 'dashboard/confirmer_suppression.html', {'mouvement': mouvement})

@login_required
def exporter_journal_excel(request):
    mouvements = MouvementFinance.objects.all().values('date', 'type', 'provenance_beneficiaire', 'description', 'montant')
    df = pd.DataFrame(list(mouvements))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Journal_Caisse.xlsx"'
    df.to_excel(response, index=False)
    return response

# --- Projets et Offres ---
@login_required
def ajouter_projet(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_projets')
    else:
        form = ProjetForm()
    return render(request, 'dashboard/ajouter_projet.html', {'form': form})

@login_required
def modifier_projet(request, id):
    projet = get_object_or_404(Projet, id=id)
    if request.method == 'POST':
        form = ProjetForm(request.POST, request.FILES, instance=projet)
        if form.is_valid():
            form.save()
            return redirect('liste_projets')
    else:
        form = ProjetForm(instance=projet)
    return render(request, 'dashboard/modifier_projet.html', {'form': form, 'projet': projet})

@login_required
def supprimer_projet(request, id):
    projet = get_object_or_404(Projet, id=id)
    if request.method == 'POST':
        projet.delete()
        return redirect('liste_projets')
    return render(request, 'dashboard/supprimer_projet.html', {'projet': projet})

@login_required
def liste_projets(request):
    projets = Projet.objects.all()
    return render(request, 'dashboard/liste_projets.html', {'projets': paginate(request, projets)})

@login_required
def detail_projet(request, id):
    projet = get_object_or_404(Projet, id=id)
    return render(request, 'dashboard/detail_projet.html', {'projet': projet, 'affectations': projet.affectation_set.all(), 'element_form': ElementProjetForm()})

@login_required
def ajouter_offre(request):
    if request.method == 'POST':
        form = OffreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_offres')
    else:
        form = OffreForm()
    return render(request, 'dashboard/ajouter_offre.html', {'form': form})

@login_required
def liste_offres(request):
    return render(request, 'dashboard/liste_offres.html', {'offres': Offre.objects.all()})

# --- Logistique & Besoins ---
@login_required
def logistique_home(request):
    return render(request, 'dashboard/logistique_home.html')

@login_required
def creer_etat_besoin(request):
    form = EtatBesoinForm(request.POST or None)
    formset = ArticleFormSet(request.POST or None)
    if form.is_valid() and formset.is_valid():
        etat = form.save()
        formset.instance = etat
        formset.save()
        return redirect('liste_etats_besoin')
    return render(request, 'dashboard/creer_etat_besoin.html', {'form': form, 'article_formset': formset})

@login_required
def liste_etats_besoin(request):
    return render(request, 'dashboard/liste_etats_besoin.html', {'etats': paginate(request, EtatBesoin.objects.all().order_by('-date'))})

@login_required
def visualiser_besoin(request, id):
    return render(request, 'dashboard/visualiser_besoin.html', {'besoin': get_object_or_404(EtatBesoin, id=id)})

@login_required
def modifier_besoin(request, id):
    besoin = get_object_or_404(EtatBesoin, id=id)
    if request.method == 'POST':
        form = EtatBesoinForm(request.POST, instance=besoin)
        if form.is_valid():
            form.save()
            return redirect('liste_etats_besoin')
    else:
        form = EtatBesoinForm(instance=besoin)
    return render(request, 'dashboard/modifier_besoin.html', {'form': form, 'besoin': besoin})

@login_required
def supprimer_besoin(request, id):
    besoin = get_object_or_404(EtatBesoin, id=id)
    if request.method == 'POST':
        besoin.delete()
        return redirect('liste_etats_besoin')
    return render(request, 'dashboard/supprimer_besoin.html', {'besoin': besoin})

@login_required
def exporter_besoin(request, format, id):
    besoin = get_object_or_404(EtatBesoin, id=id)
    response = HttpResponse(content_type=f'application/{format}')
    response['Content-Disposition'] = f'attachment; filename="besoin_{id}.{format}"'
    response.write(f"Export du besoin {id} en format {format}")
    return response

@login_required
def ajouter_materiel(request):
    form = MaterielForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('liste_materiels')
    return render(request, 'dashboard/ajouter_materiel.html', {'form': form})

@login_required
def liste_materiels(request):
    return render(request, 'dashboard/liste_materiels.html', {'materiels': paginate(request, MaterielNonConsommable.objects.all())})

@login_required
def modifier_materiel(request, id):
    materiel = get_object_or_404(MaterielNonConsommable, id=id)
    form = MaterielForm(request.POST or None, instance=materiel)
    if form.is_valid():
        form.save()
        return redirect('liste_materiels')
    return render(request, 'dashboard/modifier_materiel.html', {'form': form, 'materiel': materiel})

@login_required
def supprimer_materiel(request, id):
    materiel = get_object_or_404(MaterielNonConsommable, id=id)
    if request.method == "POST":
        materiel.delete()
        return redirect('liste_materiels')
    return render(request, 'dashboard/confirmer_suppression_materiel.html', {'materiel': materiel})

# --- Justificatifs ---
@login_required
def ajouter_justificatif(request):
    if request.method == "POST":
        form = JustificatifForm(request.POST, request.FILES)
        formset = DetailJustificatifFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            justif = form.save()
            MouvementFinance.objects.create(
                date=justif.date, 
                provenance_beneficiaire=f"Justificatif N°{justif.no_bon}",
                montant=0, 
                type='SORTIE', 
                numero_piece=justif.no_bon
            )
            formset.instance = justif
            formset.save()
            return redirect('journal_caisse')
    else:
        form = JustificatifForm()
        formset = DetailJustificatifFormSet()
    return render(request, 'dashboard/ajouter_justificatif.html', {'form': form, 'detail_formset': formset})

# --- Suivi & Évaluation (S&E) ---
@login_required
def se_home(request):
    return render(request, 'dashboard/se_home.html')

@login_required
def ajouter_tdr(request):
    if request.method == 'POST':
        form = TDRForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_tdr')
    else:
        form = TDRForm()
    return render(request, 'dashboard/ajouter_tdr.html', {'form': form})

@login_required
def liste_tdr(request):
    return render(request, 'dashboard/liste_tdr.html', {'tdrs': TermeReference.objects.all()})

@login_required
def ajouter_rapport(request):
    form = RapportMissionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('liste_rapports')
    return render(request, 'dashboard/ajouter_rapport.html', {'form': form})

@login_required
def liste_rapports(request):
    return render(request, 'dashboard/liste_rapports.html', {'rapports': paginate(request, RapportMission.objects.all())})

@login_required
def ajouter_planification(request):
    if request.method == 'POST':
        form = PlanificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_planifications')
    else:
        form = PlanificationForm()
    return render(request, 'dashboard/ajouter_planification.html', {'form': form})

@login_required
def liste_planifications(request):
    plans = Planification.objects.all().select_related('projet').order_by('-date_debut')
    return render(request, 'dashboard/liste_planifications.html', {'plans': plans})

# --- Éléments de Projet ---
@login_required
def ajouter_element(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    if request.method == 'POST':
        form = ElementProjetForm(request.POST, request.FILES)
        if form.is_valid():
            element = form.save(commit=False)
            element.projet = projet
            element.save()
    return redirect('detail_projet', id=projet.id)

@login_required
def modifier_element(request, id):
    element = get_object_or_404(ElementProjet, id=id)
    if request.method == 'POST':
        form = ElementProjetForm(request.POST, request.FILES, instance=element)
        if form.is_valid():
            form.save()
            return redirect('detail_projet', id=element.projet.id)
    else:
        form = ElementProjetForm(instance=element)
    return render(request, 'dashboard/modifier_element.html', {'form': form, 'element': element})

@login_required
def supprimer_element(request, id):
    element = get_object_or_404(ElementProjet, id=id)
    projet_id = element.projet.id
    if request.method == 'POST':
        element.delete()
        return redirect('detail_projet', id=projet_id)
    return render(request, 'dashboard/confirmer_suppression.html', {'element': element})

# --- Ressources Humaines (RH) ---
@login_required
def liste_consultants(request):
    return render(request, 'dashboard/liste_consultants.html', {'consultants': Consultant.objects.all()})

@login_required
def voir_consultant(request, id):
    consultant = get_object_or_404(Consultant, id=id)
    return render(request, 'dashboard/voir_consultant.html', {'consultant': consultant, 'affectation': consultant.affectation_set.first()})

@login_required
def ajouter_consultant(request):
    form = ConsultantForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('liste_consultants')
    return render(request, 'dashboard/ajouter_consultant.html', {'form': form})

@login_required
def modifier_consultant(request, id):
    consultant = get_object_or_404(Consultant, id=id)
    form = ConsultantForm(request.POST or None, instance=consultant)
    if form.is_valid():
        form.save()
        return redirect('liste_consultants')
    return render(request, 'dashboard/modifier_consultant.html', {'form': form, 'consultant': consultant})

@login_required
def supprimer_consultant(request, id):
    consultant = get_object_or_404(Consultant, id=id)
    if request.method == "POST":
        consultant.delete()
        return redirect('liste_consultants')
    return render(request, 'dashboard/confirmer_suppression_consultant.html', {'consultant': consultant})

@login_required
def affecter_consultant(request, id):
    consultant = get_object_or_404(Consultant, id=id)
    form = AffectationForm(request.POST or None)
    if form.is_valid():
        aff = form.save(commit=False)
        aff.consultant = consultant
        aff.save()
        return redirect('liste_consultants')
    return render(request, 'dashboard/affecter_consultant.html', {'form': form, 'consultant': consultant})

@login_required
def presence_rh(request):
    presences = PresenceJournaliere.objects.all().order_by('-date')
    if request.method == 'POST':
        form = PresenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('presence_rh')
    else:
        form = PresenceForm()
    return render(request, 'dashboard/presence.html', {'form': form, 'presences': presences})

# --- Gestion des Utilisateurs ---
@login_required
def creer_utilisateur(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role_choisi = form.cleaned_data.get('role')
            if role_choisi:
                user.profile.role = role_choisi
                user.profile.save()
            return redirect('liste_utilisateurs')
    else:
        form = CustomUserCreationForm()
    return render(request, 'dashboard/creer_utilisateur.html', {'form': form})

@login_required
def liste_utilisateurs(request):
    utilisateurs = User.objects.select_related('profile').all()
    return render(request, 'dashboard/liste_utilisateurs.html', {'utilisateurs': utilisateurs})

@login_required
def modifier_utilisateur(request, id):
    user_instance = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user_instance)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.role = form.cleaned_data.get('role')
            profile.save()
            return redirect('liste_utilisateurs')
    else:
        form = CustomUserCreationForm(instance=user_instance, initial={'role': user_instance.profile.role})
    return render(request, 'dashboard/modifier_utilisateur.html', {'form': form})

@login_required
def supprimer_utilisateur(request, id):
    user_instance = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user_instance.delete()
        return redirect('liste_utilisateurs')
    return render(request, 'dashboard/supprimer_utilisateur_confirmer.html', {'user': user_instance})

@login_required
def deconnexion(request):
    logout(request)
    return redirect('login')

# --- Connexion ---
class CustomLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if not user.is_superuser and user.groups.filter(name='Agro animateur').exists():
            return reverse_lazy('liste_formulaires_terrain')
        return reverse_lazy('home')

# --- Formulaires et Soumissions de Terrain ---
@login_required
def liste_formulaires_terrain(request):
    formulaires = FormulaireTerrain.objects.all().select_related('projet')
    return render(request, 'dashboard/liste_formulaires_terrain.html', {'formulaires': formulaires})

@login_required
def creer_formulaire_terrain(request):
    ChampFormSet = inlineformset_factory(
        FormulaireTerrain, 
        ChampFormulaire, 
        form=ChampFormulaireForm,
        extra=1,       
        min_num=1,     
        can_delete=True 
    )
    if request.method == 'POST':
        form = FormulaireTerrainForm(request.POST)
        if form.is_valid():
            formulaire = form.save()
            formset = ChampFormSet(request.POST, instance=formulaire)
            if formset.is_valid():
                formset.save()
                return redirect('liste_formulaires_terrain')
    else:
        form = FormulaireTerrainForm()
        formset = ChampFormSet()

    return render(request, 'dashboard/creer_formulaire_terrain.html', {
        'form': form,
        'formset': formset
    })

@login_required
def remplir_formulaire_terrain(request, pk):
    formulaire = get_object_or_404(FormulaireTerrain, pk=pk)
    champs = formulaire.champs.all().order_by('ordre')

    if request.method == 'POST':
        donnees_reponses = {}
        for champ in champs:
            nom_champ_form = f'champ_{champ.id}'
            if champ.type_champ == 'choix_multiple':
                valeur = request.POST.getlist(nom_champ_form)
            elif champ.type_champ in ['photo', 'signature']:
                valeur = request.FILES.get(nom_champ_form)
                valeur = valeur.name if valeur else ""
            else:
                valeur = request.POST.get(nom_champ_form, '')
            donnees_reponses[champ.libelle_question] = valeur

        SoumissionDonnee.objects.create(
            formulaire=formulaire,
            agent=request.user,
            donnees_json=donnees_reponses
        )
        return redirect('liste_formulaires_terrain')

    return render(request, 'dashboard/remplir_formulaire.html', {
        'formulaire': formulaire,
        'champs': champs
    })

@login_required
def supprimer_formulaire_terrain(request, pk):
    formulaire = get_object_or_404(FormulaireTerrain, pk=pk)
    if request.method == 'POST':
        formulaire.delete()
        return redirect('liste_formulaires_terrain')
    return render(request, 'dashboard/confirmer_suppression.html', {'formulaire': formulaire})

@login_required
def liste_toutes_soumissions(request):
    soumissions = SoumissionDonnee.objects.all().select_related('formulaire', 'agent').order_by('-date_soumission')
    return render(request, 'dashboard/toutes_soumissions.html', {'soumissions': soumissions})

@login_required
def detail_soumission(request, pk):
    soumission = get_object_or_404(SoumissionDonnee, pk=pk)
    return render(request, 'dashboard/detail_soumission.html', {'soumission': soumission})

@login_required
def modifier_formulaire_terrain(request, pk):
    formulaire = get_object_or_404(FormulaireTerrain, pk=pk)
    ChampFormSet = inlineformset_factory(
        FormulaireTerrain, 
        ChampFormulaire, 
        form=ChampFormulaireForm,
        extra=1,       
        min_num=1,     
        can_delete=True 
    )

    if request.method == 'POST':
        form = FormulaireTerrainForm(request.POST, instance=formulaire)
        formset = ChampFormSet(request.POST, instance=formulaire)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('liste_formulaires_terrain')
    else:
        form = FormulaireTerrainForm(instance=formulaire)
        formset = ChampFormSet(instance=formulaire)

    return render(request, 'dashboard/modifier_formulaire_terrain.html', {
        'form': form,
        'formset': formset,
        'formulaire': formulaire
    })