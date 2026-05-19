from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('responsable', 'Responsable de Club'),
        ('etudiant', 'Étudiant'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    telephone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profils/', blank=True, null=True)
    bio = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

class Club(models.Model):
    CATEGORIE_CHOICES = [
        ('culturel', 'Culturel'),
        ('scientifique', 'Scientifique'),
        ('sportif', 'Sportif'),
        ('artistique', 'Artistique'),
        ('autre', 'Autre'),
    ]
    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.CharField(max_length=30, choices=CATEGORIE_CHOICES, default='autre')
    logo = models.ImageField(upload_to='clubs/logos/', blank=True, null=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='clubs_geres')
    date_creation = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    def nombre_membres(self):
        return self.membres.filter(statut='accepte').count()

class Adhesion(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adhesions')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='membres')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('etudiant', 'club')

    def __str__(self):
        return f"{self.etudiant.username} → {self.club.nom} ({self.get_statut_display()})"

class Evenement(models.Model):
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]
    titre = models.CharField(max_length=200)
    description = models.TextField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='evenements')
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(max_length=200)
    capacite_max = models.IntegerField(default=50)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    image = models.ImageField(upload_to='evenements/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} - {self.club.nom}"

    def nombre_inscrits(self):
        return self.participations.filter(confirme=True).count()

    def places_disponibles(self):
        return self.capacite_max - self.nombre_inscrits()

class Participation(models.Model):
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='participations')
    date_inscription = models.DateTimeField(auto_now_add=True)
    confirme = models.BooleanField(default=True)
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('etudiant', 'evenement')

    def __str__(self):
        return f"{self.etudiant.username} → {self.evenement.titre}"
