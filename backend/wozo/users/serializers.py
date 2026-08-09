import re

from rest_framework import serializers
from models import Seller, CustomUser


def has_forbidden_chars(value: str):
    return bool(re.findall(r'[^А-Яа-яA-Za-zЁё\s\-]', value))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username',
            'last_name', 'first_name', 'third_name',
            'date_birth', 'email', 'phone_number']

    def validate(self, attrs: dict):
        name_fields = ['last_name', 'first_name', 'third_name']

        for field in name_fields:
            value = attrs.get(field)
            if value and has_forbidden_chars(value):
                raise serializers.ValidationError('ФИО должно содержать только кириллицу, либо латиницу')
            
        phone_number = attrs.get('phone_number')
        if not(phone_number is None and phone_number == ''):
            if not phone_number.isdigit():
                raise serializers.ValidationError('Номер телефона должен содержать только цифры.')
            if phone_number.startswith('7'):
                raise serializers.ValidationError('Номер телефона должен содержать в себе цифры и начинаться с 7')
        
        return attrs


class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Seller
        fields = ['user', 'status']