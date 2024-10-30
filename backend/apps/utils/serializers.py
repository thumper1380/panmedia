from rest_framework import serializers


class MainResponseSerializer(serializers.Serializer):
    """ This is a sample serializer for showing my intent"""
    success = serializers.BooleanField(
        help_text="Whether the request was successful or not.",
    )


class ErrorResponseSerializer(MainResponseSerializer):
    """ This is a sample serializer for showing my intent"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, many=False)
        self.fields['message'] = serializers.CharField(
            help_text="The error message returned by the request."
        )
        self.fields['success'].default = False


class SuccessResponseSerializer(MainResponseSerializer):
    """ This is a sample serializer for showing my intent"""

    def __init__(self, *args, other_serializer, **kwargs):
        super().__init__(*args, **kwargs, many=False)
        self.fields['data'] = other_serializer(
            help_text="The data returned by the request.",
        )
        self.fields['success'].default = True


# =============== FIELDS ===============
class StateField(serializers.CharField):
    pass


class TagField(serializers.CharField):
    pass


class IDField(serializers.IntegerField):
    pass


class StatusField(serializers.BooleanField):
    pass



class RelatedField(serializers.RelatedField):
    def __init__(self, source='name', **kwargs):
        self.source_field = source
        super().__init__(**kwargs)

    def to_representation(self, obj):
        try:
            name = getattr(obj, self.source_field)
            id_value = obj.id
        except AttributeError:
            return self.source_field  # or {}, depending on how you want to handle this case

        return {'id': id_value, 'name': name}


# create dynammic serializer that gets a model as param and returns a related model serializer in format {'id': id, 'name': name}
def create_related_model_serializer(_model, source='name'):
    if source == 'name':
        _name = serializers.CharField()
    else:
        _name = serializers.CharField(source=source)

    class RelatedModelSerializer(serializers.ModelSerializer):
        name = _name

        class Meta:
            model = _model
            fields = ('id', 'name')

    return RelatedModelSerializer


class GenericColumnSerializer(serializers.ModelSerializer):
    @classmethod
    def get_column_info(cls, filterable_fields=[]):
        model_fields = {
            field.name: field for field in cls.Meta.model._meta.get_fields()}
        serializer_instance = cls()
        columns = []

        for field_name, serializer_field in serializer_instance.fields.items():
            # Default title and type
            title = serializer_field.label or field_name.title()
            # Use the class name of the field
            field_type = type(serializer_field).__name__

            # specific case for id field
            if isinstance(serializer_field, serializers.SerializerMethodField):
                field_type = 'CharField'

            # Adjust title for fields with source attribute
            source = getattr(serializer_field, 'source', field_name)
            if source in model_fields:
                model_field = model_fields[source]
                title = model_field.verbose_name if model_field.verbose_name else title

            # Check if the field is read-only
            read_only = getattr(serializer_field, 'read_only', False)

            is_filterable = field_name in filterable_fields

            columns.append({
                'key': field_name,
                'type': field_type,
                'title': title,
                'read_only': read_only,
                "visible": True,
                "filterable": is_filterable
            })

        return columns


class DetailSerializer(GenericColumnSerializer):
    id = serializers.IntegerField(
        read_only=True, source='pk', help_text='ID', label='ID')


class ListSerializer(GenericColumnSerializer):
    id = IDField(read_only=True, label='ID', source='pk')
