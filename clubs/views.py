from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import Club, Adhesion, Evenement, Participation, Profil
from .forms import InscriptionForm, ProfilForm, ClubForm, EvenementForm

def get_role(user):
    try:
        return user.profil.role
    except:
        return 'etudiant'

# ─── AUTH ────────────────────────────────────────────────────────────────────

def accueil(request):
    clubs = Club.objects.filter(actif=True).annotate(nb_membres=Count('membres'))[:6]
    evenements = Evenement.objects.filter(statut='planifie', date_debut__gte=timezone.now()).order_by('date_debut')[:4]
    return render(request, 'clubs/accueil.html', {'clubs': clubs, 'evenements': evenements})

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès !')
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'clubs/inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'clubs/connexion.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('accueil')

# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    role = get_role(request.user)
    ctx = {'role': role}

    if role == 'admin':
        ctx['nb_clubs'] = Club.objects.count()
        ctx['nb_users'] = Profil.objects.count()
        ctx['nb_adhesions'] = Adhesion.objects.filter(statut='en_attente').count()
        ctx['nb_evenements'] = Evenement.objects.count()
        ctx['derniers_clubs'] = Club.objects.order_by('-date_creation')[:5]
        ctx['dernieres_adhesions'] = Adhesion.objects.order_by('-date_demande')[:5]

    elif role == 'responsable':
        mes_clubs = Club.objects.filter(responsable=request.user)
        ctx['mes_clubs'] = mes_clubs
        ctx['nb_membres'] = Adhesion.objects.filter(club__in=mes_clubs, statut='accepte').count()
        ctx['demandes_en_attente'] = Adhesion.objects.filter(club__in=mes_clubs, statut='en_attente').count()
        ctx['prochains_evenements'] = Evenement.objects.filter(club__in=mes_clubs, date_debut__gte=timezone.now()).order_by('date_debut')[:3]

    else:
        mes_clubs = Club.objects.filter(membres__etudiant=request.user, membres__statut='accepte')
        ctx['mes_clubs'] = mes_clubs
        ctx['mes_participations'] = Participation.objects.filter(etudiant=request.user, confirme=True).select_related('evenement')[:5]
        ctx['evenements_dispo'] = Evenement.objects.filter(statut='planifie', date_debut__gte=timezone.now()).exclude(participations__etudiant=request.user).order_by('date_debut')[:4]

    return render(request, 'clubs/dashboard.html', ctx)

# ─── PROFIL ──────────────────────────────────────────────────────────────────

@login_required
def profil(request):
    profil_obj, _ = Profil.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=profil_obj)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profil mis à jour !')
            return redirect('profil')
    else:
        form = ProfilForm(instance=profil_obj)
    return render(request, 'clubs/profil.html', {'form': form, 'profil': profil_obj})

# ─── CLUBS ───────────────────────────────────────────────────────────────────

@login_required
def liste_clubs(request):
    clubs = Club.objects.filter(actif=True).annotate(nb_membres=Count('membres'))
    mes_adhesions = Adhesion.objects.filter(etudiant=request.user).values_list('club_id', 'statut')
    adhesions_dict = {cid: stat for cid, stat in mes_adhesions}
    return render(request, 'clubs/liste_clubs.html', {'clubs': clubs, 'adhesions_dict': adhesions_dict})

@login_required
def detail_club(request, pk):
    club = get_object_or_404(Club, pk=pk)
    membres = Adhesion.objects.filter(club=club, statut='accepte').select_related('etudiant')
    evenements = Evenement.objects.filter(club=club).order_by('-date_debut')
    adhesion = Adhesion.objects.filter(etudiant=request.user, club=club).first()
    return render(request, 'clubs/detail_club.html', {'club': club, 'membres': membres, 'evenements': evenements, 'adhesion': adhesion})

@login_required
def creer_club(request):
    if get_role(request.user) not in ['admin', 'responsable']:
        messages.error(request, 'Accès refusé.')
        return redirect('liste_clubs')
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save(commit=False)
            club.responsable = request.user
            club.save()
            messages.success(request, f'Club "{club.nom}" créé avec succès !')
            return redirect('detail_club', pk=club.pk)
    else:
        form = ClubForm()
    return render(request, 'clubs/form_club.html', {'form': form, 'titre': 'Créer un club'})

@login_required
def modifier_club(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if get_role(request.user) == 'admin' or club.responsable == request.user:
        if request.method == 'POST':
            form = ClubForm(request.POST, request.FILES, instance=club)
            if form.is_valid():
                form.save()
                messages.success(request, 'Club modifié !')
                return redirect('detail_club', pk=club.pk)
        else:
            form = ClubForm(instance=club)
        return render(request, 'clubs/form_club.html', {'form': form, 'titre': 'Modifier le club'})
    messages.error(request, 'Accès refusé.')
    return redirect('liste_clubs')

@login_required
def supprimer_club(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if get_role(request.user) == 'admin':
        club.delete()
        messages.success(request, 'Club supprimé.')
    return redirect('liste_clubs')

# ─── ADHÉSIONS ───────────────────────────────────────────────────────────────

@login_required
def demander_adhesion(request, club_pk):
    club = get_object_or_404(Club, pk=club_pk)
    adhesion, created = Adhesion.objects.get_or_create(etudiant=request.user, club=club)
    if created:
        messages.success(request, f'Demande d\'adhésion envoyée au club "{club.nom}".')
    else:
        messages.info(request, 'Vous avez déjà une demande pour ce club.')
    return redirect('detail_club', pk=club_pk)

@login_required
def gerer_adhesions(request, club_pk):
    club = get_object_or_404(Club, pk=club_pk)
    if get_role(request.user) != 'admin' and club.responsable != request.user:
        messages.error(request, 'Accès refusé.')
        return redirect('liste_clubs')
    adhesions = Adhesion.objects.filter(club=club).select_related('etudiant').order_by('-date_demande')
    return render(request, 'clubs/gerer_adhesions.html', {'club': club, 'adhesions': adhesions})

@login_required
def traiter_adhesion(request, pk, action):
    adhesion = get_object_or_404(Adhesion, pk=pk)
    if get_role(request.user) == 'admin' or adhesion.club.responsable == request.user:
        if action == 'accepter':
            adhesion.statut = 'accepte'
            messages.success(request, f'{adhesion.etudiant.get_full_name()} a été accepté.')
        elif action == 'refuser':
            adhesion.statut = 'refuse'
            messages.info(request, f'Demande de {adhesion.etudiant.get_full_name()} refusée.')
        adhesion.date_traitement = timezone.now()
        adhesion.save()
    return redirect('gerer_adhesions', club_pk=adhesion.club.pk)

# ─── ÉVÉNEMENTS ──────────────────────────────────────────────────────────────

@login_required
def liste_evenements(request):
    evenements = Evenement.objects.select_related('club').order_by('-date_debut')
    mes_participations = Participation.objects.filter(etudiant=request.user).values_list('evenement_id', flat=True)
    return render(request, 'clubs/liste_evenements.html', {'evenements': evenements, 'mes_participations': mes_participations})

@login_required
def creer_evenement(request, club_pk):
    club = get_object_or_404(Club, pk=club_pk)
    if get_role(request.user) != 'admin' and club.responsable != request.user:
        messages.error(request, 'Accès refusé.')
        return redirect('liste_evenements')
    if request.method == 'POST':
        form = EvenementForm(request.POST, request.FILES)
        if form.is_valid():
            evt = form.save(commit=False)
            evt.club = club
            evt.save()
            messages.success(request, f'Événement "{evt.titre}" créé !')
            return redirect('liste_evenements')
    else:
        form = EvenementForm()
    return render(request, 'clubs/form_evenement.html', {'form': form, 'club': club, 'titre': 'Créer un événement'})

@login_required
def inscrire_evenement(request, pk):
    evt = get_object_or_404(Evenement, pk=pk)
    if evt.places_disponibles() > 0:
        participation, created = Participation.objects.get_or_create(etudiant=request.user, evenement=evt)
        if created:
            messages.success(request, f'Inscrit à "{evt.titre}" !')
        else:
            messages.info(request, 'Vous êtes déjà inscrit.')
    else:
        messages.error(request, 'Plus de places disponibles.')
    return redirect('liste_evenements')

@login_required
def annuler_participation(request, pk):
    participation = get_object_or_404(Participation, pk=pk, etudiant=request.user)
    participation.delete()
    messages.info(request, 'Participation annulée.')
    return redirect('liste_evenements')

# ─── ADMIN ───────────────────────────────────────────────────────────────────

@login_required
def gerer_utilisateurs(request):
    if get_role(request.user) != 'admin':
        return redirect('dashboard')
    profils = Profil.objects.select_related('user').all()
    return render(request, 'clubs/gerer_utilisateurs.html', {'profils': profils})

@login_required
def changer_role(request, user_pk, role):
    if get_role(request.user) != 'admin':
        return redirect('dashboard')
    profil_obj = get_object_or_404(Profil, user__pk=user_pk)
    if role in ['admin', 'responsable', 'etudiant']:
        profil_obj.role = role
        profil_obj.save()
        messages.success(request, f'Rôle mis à jour pour {profil_obj.user.get_full_name()}.')
    return redirect('gerer_utilisateurs')

@login_required
def statistiques(request):
    if get_role(request.user) != 'admin':
        return redirect('dashboard')
    ctx = {
        'nb_clubs': Club.objects.count(),
        'nb_users': Profil.objects.count(),
        'nb_evenements': Evenement.objects.count(),
        'nb_participations': Participation.objects.count(),
        'clubs_par_categorie': Club.objects.values('categorie').annotate(total=Count('id')),
        'top_clubs': Club.objects.annotate(nb=Count('membres')).order_by('-nb')[:5],
    }
    return render(request, 'clubs/statistiques.html', ctx)
