from django.contrib import admin
from quiz.models import (
    Question, Answer, Quiz, QuizResult
)


class AnswerInline(admin.TabularInline):
    extra = 3
    max_num = 3
    model = Answer

    raw_id_fields = ['creator']
    readonly_fields = ('creator', 'editor', 'datetime_created', 'datetime_modified')


class QuestionAdmin(admin.ModelAdmin):
    raw_id_fields = ['creator']
    readonly_fields = ('creator', 'editor', 'datetime_created', 'datetime_modified')
    inlines = [AnswerInline]
    list_display = ['question', 'difficulty', 'creator', 'datetime_created',
                    'is_active']
    list_editable = ['is_active', 'difficulty']
    date_hierarchy = "datetime_created"
    search_fields = ('question',)
    list_filter = ('is_active', 'creator',)


class AnswerAdmin(admin.ModelAdmin):
    raw_id_fields = ['creator']
    readonly_fields = ('creator', 'editor', 'datetime_created', 'datetime_modified')
    list_display = ['answer', 'creator', 'datetime_created', 'is_active']
    list_editable = ['is_active']
    date_hierarchy = "datetime_created"
    search_fields = ('answer',)
    list_filter = ('is_active', 'creator',)


class QuizAdmin(admin.ModelAdmin):
    raw_id_fields = ['creator']
    readonly_fields = ('creator', 'editor', 'datetime_created', 'datetime_modified')
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ['questions']
    list_display = ['name', 'creator', 'datetime_created', 'status']
    list_editable = ['status']
    date_hierarchy = "datetime_created"
    search_fields = ('name',)
    list_filter = ('status', 'creator',)


class QuizResultAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    fieldsets = (
        (None, {
            'fields': ('quiz', 'user', 'email', ('score', 'maximum_score')),
        }),
        ('Answers Provided', {
            'fields': ('answers',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('creator', 'editor', 'datetime_created', 'datetime_modified')
        }),
    )
    readonly_fields = ('creator', 'editor', 'datetime_created', 'datetime_modified')
    date_hierarchy = "datetime_created"
    filter_vertical = ['answers']
    list_display = ['user', 'email', 'datetime_created', 'score', 'maximum_score']
    list_display = ['quiz', 'user', 'email', 'datetime_created', 'score',
                    'maximum_score']
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'email')
    list_filter = ('datetime_created',)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizResult, QuizResultAdmin)

