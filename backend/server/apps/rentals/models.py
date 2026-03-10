from django.db import models


class TarrifTypeEnum(models.TextChoices):
    PER_MINUTE = "PER_MINUTE", "Per Minute"
    PER_HOUR = "PER_HOUR", "Per Hour"
    PER_DAY = "PER_DAY", "Per Day"
    FIXED = "FIXED", "Fixed"


class TariffModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price_per_tick = models.PositiveIntegerField(null=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class RentalModel(models.Model):
    user = models.ForeignKey(
        "users.UserModel",
        on_delete=models.PROTECT,
        related_name="rentals",
    )
    battery = models.ForeignKey(
        "stantions.RegisteredBatteryModel",
        on_delete=models.PROTECT,
        related_name="rentals",
    )
    tariff = models.ForeignKey(
        TariffModel,
        on_delete=models.PROTECT,
        related_name="rentals",
    )
    started_at_stantion = models.ForeignKey(
        "stantions.RegisteredStantionModel",
        on_delete=models.PROTECT,
        related_name="rentals_as_start",
    )
    completed_at_stantion = models.ForeignKey(
        "stantions.RegisteredStantionModel",
        on_delete=models.PROTECT,
        related_name="rentals_as_end",
        null=True,
        blank=True,
    )

    final_price = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=255)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
