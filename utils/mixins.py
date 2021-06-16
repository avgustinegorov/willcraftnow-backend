class ListSerializerWithChildModelsMixin:

    def get_child_serializer(self, instance):
        serializer_map = self.Meta.serializer_map
        child_instance = self.get_child_instance(instance)
        type_key = self.get_type_key(instance)
        serializer = serializer_map[type_key]
        return serializer(instance, context=self.context)

    def get_child_instance(self, instance):
        type_key = self.get_type_key(instance)
        return getattr(instance, type_key.lower())

    def get_type_key(self, instance):
        model_key = self.Meta.model_key
        return getattr(instance, model_key)

    def to_internal_value(self, data):
        # print('internal value', data)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        # print('representation', instance)
        return self.get_child_serializer(instance).to_representation(self.get_child_instance(instance))


class DisplayValuesMixin:

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not self.context.get('show_display', False):
            return ret
        fields = getattr(self.Meta, 'display_fields', [])
        for field_name in fields:
            ret[field_name] = getattr(instance, f'get_{field_name}_display')()
        return ret
