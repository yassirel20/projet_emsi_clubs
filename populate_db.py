import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_clubs.settings')
django.setup()

from django.contrib.auth.models import User
from clubs.models import Profil, Club, Adhesion, Evenement, Participation
from django.utils import timezone
from datetime import timedelta

print("🔄 Création des données de démonstration...")

# Supprimer les données existantes
Participation.objects.all().delete()
Adhesion.objects.all().delete()
Evenement.objects.all().delete()
Club.objects.all().delete()
Profil.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# ── UTILISATEURS ──
admin_user = User.objects.create_user('admin', 'admin@campus.ma', 'admin123', first_name='Ahmed', last_name='Benali')
Profil.objects.create(user=admin_user, role='admin', telephone='0600000001')

resp1 = User.objects.create_user('resp_sarah', 'sarah@campus.ma', 'resp123', first_name='Sarah', last_name='El Mansouri')
Profil.objects.create(user=resp1, role='responsable', telephone='0600000002')

resp2 = User.objects.create_user('resp_karim', 'karim@campus.ma', 'resp123', first_name='Karim', last_name='Ouhabi')
Profil.objects.create(user=resp2, role='responsable', telephone='0600000003')

students = []
noms = [
    ('Fatima', 'Zahra', 'fatimazahra'), ('Yassine', 'Belkasmi', 'yassine'),
    ('Nadia', 'Chraibi', 'nadia'), ('Omar', 'Tazi', 'omar'),
    ('Laila', 'Bensouda', 'laila'), ('Mehdi', 'Alaoui', 'mehdi'),
]
for prenom, nom, username in noms:
    u = User.objects.create_user(username, f'{username}@campus.ma', 'etud123', first_name=prenom, last_name=nom)
    Profil.objects.create(user=u, role='etudiant')
    students.append(u)

# ── CLUBS ──
clubs_data = [
    ('Club Informatique & IA', 'Club dédié à la programmation, l\'intelligence artificielle et aux nouvelles technologies. Nous organisons des hackathons, ateliers et conférences tech.', 'scientifique', resp1),
    ('Club Théâtre & Arts', 'Espace d\'expression artistique et théâtrale. Rejoignez-nous pour explorer votre créativité à travers les arts de la scène.', 'culturel', resp2),
    ('Club Sportif Emsi', 'Club multisports ouvert à tous : football, basketball, tennis de table. Compétitions inter-universités et entraînements hebdomadaires.', 'sportif', resp1),
    ('Club Entrepreneuriat', 'Accompagnement des étudiants entrepreneurs : ateliers business plan, pitch, mentorat et networking avec des professionnels.', 'scientifique', resp2),
    ('Club Photo & Vidéo', 'Apprenez la photographie et le montage vidéo. Sorties photo, workshops et expositions sur le campus.', 'artistique', resp1),
]

clubs = []
for nom, desc, cat, resp in clubs_data:
    club = Club.objects.create(nom=nom, description=desc, categorie=cat, responsable=resp)
    clubs.append(club)

# ── ADHÉSIONS ──
adhesions_data = [
    (students[0], clubs[0], 'accepte'), (students[1], clubs[0], 'accepte'),
    (students[2], clubs[0], 'en_attente'), (students[3], clubs[1], 'accepte'),
    (students[4], clubs[1], 'accepte'), (students[0], clubs[2], 'accepte'),
    (students[5], clubs[2], 'en_attente'), (students[1], clubs[3], 'accepte'),
    (students[2], clubs[3], 'accepte'), (students[3], clubs[4], 'refuse'),
    (students[4], clubs[4], 'accepte'),
]
for etudiant, club, statut in adhesions_data:
    Adhesion.objects.create(etudiant=etudiant, club=club, statut=statut)

# ── ÉVÉNEMENTS ──
now = timezone.now()
events_data = [
    ('Hackathon IA 2024', 'Compétition de 24h pour développer des solutions basées sur l\'IA. Prix à gagner !', clubs[0], now + timedelta(days=7), now + timedelta(days=8), 'Salle Informatique B3', 30),
    ('Atelier Python Avancé', 'Maîtrisez Django, FastAPI et les bonnes pratiques de développement Python.', clubs[0], now + timedelta(days=3), now + timedelta(days=3, hours=3), 'Amphithéâtre 2', 50),
    ('Spectacle de Fin d\'Année', 'Grand spectacle théâtral préparé tout au long de l\'année. Entrée libre pour les étudiants.', clubs[1], now + timedelta(days=14), now + timedelta(days=14, hours=2), 'Salle des Fêtes', 150),
    ('Tournoi de Football', 'Tournoi inter-facultés. Inscrivez votre équipe de 7 joueurs et disputez le trophée.', clubs[2], now + timedelta(days=5), now + timedelta(days=5, hours=4), 'Terrain de Sport A', 80),
    ('Conférence Entrepreneuriat', 'Table ronde avec des entrepreneurs locaux. Comment lancer sa startup en étant étudiant ?', clubs[3], now + timedelta(days=10), now + timedelta(days=10, hours=2), 'Amphithéâtre Principal', 100),
    ('Sortie Photo Médina', 'Sortie photographique dans la médina historique. Apportez votre appareil photo.', clubs[4], now + timedelta(days=2), now + timedelta(days=2, hours=5), 'Médina de Rabat', 20),
    ('Workshop Montage Vidéo', 'Initiation à Adobe Premiere Pro et DaVinci Resolve.', clubs[4], now - timedelta(days=5), now - timedelta(days=5, hours=3), 'Labo Multimédia', 15),
]
events = []
for titre, desc, club, debut, fin, lieu, cap in events_data:
    statut = 'termine' if debut < now else 'planifie'
    e = Evenement.objects.create(titre=titre, description=desc, club=club, date_debut=debut, date_fin=fin, lieu=lieu, capacite_max=cap, statut=statut)
    events.append(e)

# ── PARTICIPATIONS ──
Participation.objects.create(etudiant=students[0], evenement=events[0])
Participation.objects.create(etudiant=students[1], evenement=events[0])
Participation.objects.create(etudiant=students[2], evenement=events[1])
Participation.objects.create(etudiant=students[3], evenement=events[3])
Participation.objects.create(etudiant=students[4], evenement=events[4])

# Superuser
if not User.objects.filter(username='superadmin').exists():
    User.objects.create_superuser('superadmin', 'super@campus.ma', 'super123')

print("✅ Base de données peuplée avec succès !")
print("\n📋 Comptes de test :")
print("  Admin      → admin / admin123")
print("  Responsable 1 → resp_sarah / resp123")
print("  Responsable 2 → resp_karim / resp123")
print("  Étudiant   → fatimazahra / etud123")
print("  Superadmin Django → superadmin / super123")
