from django.contrib.auth.models import User
from django.db.models.signals import post_save

from quiz.models import QuizResult

def update_quiz_results(sender, instance, created, **kwargs):
    """When a user registers, check to see if they had any previous quiz
    results under their email-address. If so, modify them so that they now
    point to this user."""
    if created:
        quiz_results = QuizResult.objects.filter(
            email=instance.email, user=None).update(user=instance)

def start_listening():
    """Import this function in a models file and call it to activate the above
    listener."""
    post_save.connect(update_quiz_results, sender=User)

def stop_listening():
    """Inverse of start_listening."""
    post_save.disconnect(update_quiz_results, sender=User)
