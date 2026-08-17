import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Seller


CustomUser = get_user_model()


def has_forbidden_chars(value: str):
    return bool(re.findall(r'[^А-Яа-яA-Za-zЁё\s\-]', value))


class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'last_name', 'first_name', 'third_name',
            'date_birth', 'email', 'phone_number', 'confirm_password']

    def validate_password(self, value):
        validate_password(value)

        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('Пароли не совпадают.')
        return super().validate(attrs)

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'], first_name=validated_data['first_name'],
            last_name=validated_data['last_name'], third_name=validated_data['third_name'],
            date_birth=validated_data['date_birth'], email=validated_data['email'],
            phone_number=validated_data['phone_number'], password=validated_data['password'])
        return user


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
        
        return attrs


class SellerRegistrationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Seller
        fields = ('user', 'status', 'status_display')
        extra_kwargs = {
            'user': {'read_only': True}}


    def validate(self, attrs: dict):
        user = self.context['request'].user

        if Seller.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже зарегестрированы как продавец.'})
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Seller
        fields = ['user', 'id', 'status']