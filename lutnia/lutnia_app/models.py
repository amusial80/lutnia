from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse  
from django.core.files.storage import default_storage
from PIL import Image
from django.utils._os import safe_join
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #file_path = safe_join(settings.MEDIA_ROOT, "profile_pics/default.png")
    #print(f'SCIEZKA DO PLIKU TO: {file_path}')
    image = models.ImageField(default="profile_pics/default.png", upload_to="profile_pics/")
    user_code = models.CharField(max_length=2, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name} Profile'

    def save(self, *args, **kwargs):
        #default_profile_image = safe_join(settings.MEDIA_ROOT, "profile_pics/default.png")
        """Delete the old image when updating the profile image (except the default image)."""
        try:
            old_profile = Profile.objects.get(pk=self.pk)  # Get existing profile instance
            if old_profile.image and old_profile.image != self.image:
                if old_profile.image.name != "profile_pics/default.png":  # Avoid deleting default image
                    if default_storage.exists(old_profile.image.name):
                        default_storage.delete(old_profile.image.name)  # Delete old image
        except Profile.DoesNotExist:
            pass  # If profile doesn't exist yet, do nothing

        super().save(*args, **kwargs)  # Save new image
        img = Image.open(self.image.path)  # Open image
        if img.height > 300 or img.width > 300:  # Resize if too large
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)  # Overwrite saved image
    
    def delete(self, *args, **kwargs):
        """Delete image file when deleting the profile (except the default image)."""
        if self.image and self.image.name != 'profile_pics/default.png':
            if default_storage.exists(self.image.name):
                default_storage.delete(self.image.name)
        super().delete(*args, **kwargs)

# Signal to delete the image when the profile is deleted
@receiver(models.signals.post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes image file from storage when the Profile object is deleted."""
    if instance.image and instance.image.name != 'profile_pics/default.png':
        if default_storage.exists(instance.image.name):
            default_storage.delete(instance.image.name)
   
class YTVideo(models.Model):
    link = models.URLField()
    def __unicode__(self):
        return self.link

class Event(models.Model):
    PLACE_CHOICES = [
        ('1', 'Moniuszki'),
        ('2', 'Laska'),
    ]

    TABLE_CHOICES = [
        ('1', 'Snooker nr.1'),
        ('2', 'Snooker nr.2'),
        ('3', 'Pool nr.1'),
        ('4', 'Pool nr.2'),
        ('5', 'Snooker nr.3'),
        ('6', 'Snooker nr.4'),
        ('7', 'Snooker nr.5'),
    ]

    TABLE_CHOICES_LUTNIA =[
        ('5', 'Snooker nr.3'),
        ('6', 'Snooker nr.4'),
        ('7', 'Snooker nr.5'),
    ]

    BOOKING_TYPE_CHOICES = [
        ("1", "Liga"),
        ("2", "Turniej"),
        ("3", "Trening"),
        ("4", "Moge z kims ragrac"),
        ("5", "Rezerwuje dla 2 osob"),
        ("6", "Szkolka Dorosli"),
        ("7", "Szkolka Dzieci"),
        ("8", "Brak mozliwosci"), 
    ]

    place = models.CharField(max_length=100, default='Moniuszki', choices=PLACE_CHOICES)
    table = models.CharField(max_length=100, default='Sonnker nr.1' , choices=TABLE_CHOICES)
    bookingtype = models.CharField(max_length=100, default='Liga', choices=BOOKING_TYPE_CHOICES)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    confirmed = models.BooleanField(default=True)
    @property
    def get_html_url(self):
        url = reverse('event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.user.last_name} {self.user.first_name}</a>'
    
    def __str__(self):
        dejt = self.start_time.strftime("%Y-%B-%A-%d")
        plejs = dict(self.PLACE_CHOICES).get(self.place, self.place)
        bt = dict(self.BOOKING_TYPE_CHOICES).get(self.bookingtype, self.bookingtype)
        return f'{self.user.last_name} {self.user.first_name} {dejt} {plejs} {bt}'
   