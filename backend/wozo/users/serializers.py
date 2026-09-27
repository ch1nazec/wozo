import re

from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import Seller, PersonalData, Agent


CustomUser = get_user_model()


def has_forbidden_chars(value: str):
    return bool(re.findall(r'[^А-Яа-яA-Za-zЁё\s\-]', value))

def has_digits(value: str) -> bool:
    return value.isdigit()

def has_check_len(value: str, length: int) -> bool:
    return len(value) == length


def digits_of_length(length, field_name):
    def validator(value):
        if not has_check_len(value, length):
            raise serializers.ValidationError(
                f'{field_name} должен состоять из {length} цифр.'
            )
        if not has_digits(value):
            raise serializers.ValidationError(
                f'{field_name} должен состоять только из цифр.'
            )
        return value
    return validator


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    'User not found.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Введите почту и пароль.'
            )


class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'last_name', 'first_name', 'third_name', 'password',
            'date_birth', 'email', 'phone_number', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('Пароли не совпадают.')
        return super().validate(attrs)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
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


PERSONAL_DATA_FIELDS = (
    'user', 'inn', 'snils',
    'passport_series', 'passport_number',
    'passport_issued_by', 'passport_issued_date',
)

class PersonalDataRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    inn = serializers.CharField(
        validators=[digits_of_length(12, 'ИНН')]
    )
    snils = serializers.CharField(
        validators=[digits_of_length(11, 'СНИЛС')]
    )
    passport_series = serializers.CharField(
        validators=[digits_of_length(4, 'Серия паспорта')]
    )
    passport_number = serializers.CharField(
        validators=[digits_of_length(6, 'Номер паспорта')]
    )

    class Meta:
        model = PersonalData
        fields = PERSONAL_DATA_FIELDS


class PersonalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalData
        fields = ('id',) + PERSONAL_DATA_FIELDS


class AgentSerializerRegistration(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('id', 'is_active')
        read_only_fields = ('id',)

    def validate(self, attrs):
        request = self.context.get('request')
        try:
            request.user.personal_data
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Сначала заполните персональные данные.'
            )
        return attrs

    def create(self, validated_data):
        validated_data['personal_data'] = self.context['request'].user.personal_data
        return super().create(validated_data)


class AgentSerializer(serializers.ModelSerializer):
    personal_data = PersonalDataSerializer(read_only=True)

    class Meta:
        model = Agent
        fields = ('id', 'personal_data', 'is_active')