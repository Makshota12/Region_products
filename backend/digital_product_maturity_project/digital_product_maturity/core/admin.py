from django.contrib import admin
from .models import (
    Product,
    Domain,
    Criterion,
    RatingScale,
    EvaluationSession,
    AssignedCriterion,
    EvaluationAnswer,
    Role,
    Profile,
)


class RatingScaleInline(admin.TabularInline):
    model = RatingScale
    extra = 0


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name", "weight")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "weight")
    list_filter = ("domain",)
    search_fields = ("name", "domain__name")
    ordering = ("domain__name", "name")
    inlines = [RatingScaleInline]


@admin.register(RatingScale)
class RatingScaleAdmin(admin.ModelAdmin):
    list_display = ("criterion", "score")
    list_filter = ("criterion__domain", "criterion")
    search_fields = ("criterion__name", "description")
    ordering = ("criterion__domain__name", "criterion__name", "score")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "department_owner", "launch_date", "is_archived")
    list_filter = ("is_archived", "launch_date")
    search_fields = ("name", "department_owner", "description")
    ordering = ("name",)


class AssignedCriterionInline(admin.TabularInline):
    model = AssignedCriterion
    extra = 0
    autocomplete_fields = ("criterion", "assigned_to")
    show_change_link = True


@admin.register(EvaluationSession)
class EvaluationSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "status", "created_by", "start_date", "end_date")
    list_filter = ("status", "start_date", "product")
    search_fields = ("product__name", "created_by__username")
    ordering = ("-start_date", "-id")
    autocomplete_fields = ("product", "created_by")
    inlines = [AssignedCriterionInline]


class EvaluationAnswerInline(admin.StackedInline):
    model = EvaluationAnswer
    extra = 0


@admin.register(AssignedCriterion)
class AssignedCriterionAdmin(admin.ModelAdmin):
    list_display = ("id", "evaluation_session", "criterion", "assigned_to", "is_verified")
    list_filter = ("is_verified", "criterion__domain", "evaluation_session__status")
    search_fields = (
        "criterion__name",
        "evaluation_session__product__name",
        "assigned_to__username",
    )
    ordering = ("-evaluation_session__start_date", "criterion__domain__name", "criterion__name")
    autocomplete_fields = ("evaluation_session", "criterion", "assigned_to")
    inlines = [EvaluationAnswerInline]


@admin.register(EvaluationAnswer)
class EvaluationAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "assigned_criterion", "score_value", "metric_value", "submitted_at")
    list_filter = (
        "submitted_at",
        "assigned_criterion__criterion__domain",
        "assigned_criterion__evaluation_session__status",
    )
    search_fields = (
        "assigned_criterion__criterion__name",
        "assigned_criterion__evaluation_session__product__name",
        "comment",
    )
    ordering = ("-submitted_at",)
    autocomplete_fields = ("assigned_criterion",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "role")
