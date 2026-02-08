import random
from django.utils import timezone


def generate_otp():
    return str(random.randint(100000, 999999))
