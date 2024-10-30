from rest_framework import viewsets, filters
from django.db.models import Q
from rest_framework.response import Response


class SearchMultipleModelsViewSet(viewsets.GenericViewSet):
    models = []  # List of Django Model classes
    serializers = []  # List of corresponding serializers
    search_fields = []  # Shared list of search fields

    def _get_queryset_mappings(self) -> dict:
        queryset_mappings = {}
        for idx, Model in enumerate(self.models):
            model_name = Model.__name__
            serializer_class = self.serializers[idx]

            # Filter search fields based on the fields available in the model
            model_search_fields = [field for field in self.search_fields if field in [
                f.name for f in Model._meta.fields]]

            queryset_mappings[model_name] = {
                'queryset': Model.objects.all(),
                'serializer': serializer_class,
                'search_fields': model_search_fields
            }
        return queryset_mappings

    def list(self, request, *args, **kwargs):
        search_term = request.query_params.get('q', None)
        results = {}

        for model_name, config in self._get_queryset_mappings().items():
            queryset = config['queryset']
            search_fields = config['search_fields']
            serializer_class = config['serializer']

            if search_term and search_fields:
                query = Q()
                for field in search_fields:
                    query |= Q(**{f'{field}__icontains': search_term})
                queryset = queryset.filter(query)

            results[model_name] = serializer_class(queryset, many=True).data

        return Response(results)
