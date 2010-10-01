from quiz.models import Question

def get_display_name(difficulty):
    for value, display in Question.DIFFICULTY_CHOICES:
        if value == difficulty:
            return display
