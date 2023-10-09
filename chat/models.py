from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class Sector(models.Model):
    name = models.CharField(max_length=54)

    def __str__(self):
        return self.name


class Button(models.Model):
    body = models.CharField(max_length=96)

    def __str__(self):
        return f"{self.id} - {self.body}"


class HighStructuredMessage(models.Model):
    name = models.CharField(
        max_length=512,
    )
    body = models.TextField(
        max_length=1052,
    )
    header = models.CharField(max_length=256, null=True, blank=True)
    footer = models.CharField(max_length=256, null=True, blank=True)
    buttons = models.ManyToManyField(to=Button)
    header_variables_quantity = models.IntegerField(default=0)
    body_variables_quantity = models.IntegerField(default=0)
    language_code = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.name


class WhatsAppPOST(models.Model):
    body = models.CharField(max_length=564)


class Contact(models.Model):
    name = models.CharField(max_length=96, blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    customer_phone_number = models.CharField(max_length=13)
    customer_name = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, blank=True, null=True)

    def finish_attendance(self):
        self.is_close = True
        self.closed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.customer_name} - {self.customer_phone_number} - {self.id}"


class Message(models.Model):
    whatsapp_message_id = models.CharField(max_length=264, default="")
    send_by_operator = models.BooleanField(default=False)
    body = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    type = models.CharField(max_length=24, blank=True, null=True)
    media_id = models.CharField(max_length=255, blank=True, null=True)
    media = models.FileField(upload_to="media", blank=True, null=True)
    contacts = models.ManyToManyField(Contact, "contacts", blank=True)
    context = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )
    origin_identifier = models.CharField(max_length=13, blank=True, null=True)
    attendance = models.ForeignKey(
        Attendance,
        related_name="messages",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"ID:{self.id} --> {self.body} enviada em {self.created_at}"


@receiver(pre_save, sender=Message)
def link_message_to_last_open_attendance(sender, instance, **kwargs):
    phone_number = instance.origin_identifier
    last_open_attendance = Attendance.objects.filter(
        customer_phone_number=phone_number, is_closed=False
    ).last()

    if last_open_attendance is not None:
        instance.attendance = last_open_attendance

    else:
        contact_info = Contact.objects.filter(phone=phone_number).first()
        print(f"CONTACT INFO {contact_info}")
        Attendance.objects.create(
            customer_phone_number=contact_info.phone,
            customer_name=contact_info.name,
        )
    print(f"INSTANCIA --> {instance} FILTERED ATTENDANCE {last_open_attendance}")
