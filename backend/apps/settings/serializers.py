# import serializers
import re
from phonenumber_field.serializerfields import PhoneNumberField as _PhoneNumberField
from django.utils.text import slugify
from django.db.models import F
from rest_framework import serializers
from .models import Form, LeadFlow, LeadProfile, ValidationRule, SaleStatus


class LeadFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadFlow
        fields = '__all__'


class ValidationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationRule
        fields = ['name', 'rule_type', 'rule_parameters']


class LeadProfileSerializer(serializers.ModelSerializer):
    validation_rules = ValidationRuleSerializer(many=True, read_only=True)

    class Meta:
        model = LeadProfile
        fields = ['type', 'label', 'key', 'place_holder',
                  'autocomplete', 'pattern', 'validation_rules', 'position']


class FormSerializer(serializers.ModelSerializer):
    fields = LeadProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ['name', 'header', 'submit_button_text',
                  'toc', 'created_at', 'updated_at', 'fields']


class SaleStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleStatus
        fields = ['name', 'description', 'key', 'color',]


class PhoneNumberField(_PhoneNumberField):
    def to_internal_value(self, data):
        if not re.match(r'^\+?[1-9]\d{1,14}$', data):
            raise serializers.ValidationError(self.error_messages["invalid"])
        return super().to_internal_value(data)


def create_form_serializer(form: Form):
    class_name = f"{slugify(form.name).replace('-', '_').capitalize()}Serializer"
    fields = {field.key: create_serializer_field(
        field) for field in form.fields.all()}
    Meta = type('Meta', (), {'model': LeadProfile,
                'fields': list(fields.keys())})
    serializer_class = type(class_name, (serializers.ModelSerializer,), {
                            'Meta': Meta, **fields})
    return serializer_class


def create_serializer_field(field):
    field_type = field.type
    field_options = {
        'label': field.label,
        'required': field.validation_rules.filter(rule_type='required').exists(),
        'allow_blank': not field.validation_rules.filter(rule_type='required').exists(),
    }
    if field_type == LeadProfile.FieldTypeChoices.TEXT:
        return serializers.CharField(**field_options)
    elif field_type == LeadProfile.FieldTypeChoices.EMAIL:
        return serializers.EmailField(**field_options)
    elif field_type == LeadProfile.FieldTypeChoices.NUMBER:
        return serializers.IntegerField(**field_options)
    elif field_type == LeadProfile.FieldTypeChoices.TEL:
        return PhoneNumberField(**field_options)

    # not implemented
    raise NotImplementedError(f"Field type {field_type} not implemented")
