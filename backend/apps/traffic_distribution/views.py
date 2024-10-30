from rest_framework.decorators import action
from .serializers import ReadFolderPolymorphicSerializer, WriteFolderPolymorphicSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Advertiser, RotationControl
from .serializers import AdvertiserDetailSerializer, BaseFolderSerializer
from apps.utils.responses import SuccessResponse, ErrorResponse
from rest_framework import status, response

# def retrieve(self, request, pk=None):
#     queryset = TrafficData.objects.all()
#     traffic_data = get_object_or_404(queryset, pk=pk)
#     cols = TrafficDataDetailSerializer.get_column_info()
#     return SuccessResponse(data=TrafficDataDetailSerializer(traffic_data).data, columns=cols)


class AdvertiserViewSet(ModelViewSet):
    queryset = Advertiser.objects.all()
    serializer_class = AdvertiserDetailSerializer
    permission_classes = []
    authentication_classes = []

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cols = AdvertiserDetailSerializer.get_column_info()
        return SuccessResponse(data=serializer.data, columns=cols)


class RotationControlViewSet(ModelViewSet):
    queryset = RotationControl.objects.all()
    serializer_class = ReadFolderPolymorphicSerializer
    permission_classes = []
    authentication_classes = []

    def retrieve(self, request, *args, **kwargs):
        folder = self.get_object()
        serializer = ReadFolderPolymorphicSerializer(folder)
        return SuccessResponse(data=serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = RotationControl.objects.root_nodes()
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data)

    @action(detail=True, methods=['patch'], url_path='set-active', url_name='set-active')
    def set_active(self, request, *args, **kwargs):
        folder = self.get_object()
        is_active = request.data.get('is_active', None)

        folder.set_active(is_active, set_children=True)

        return SuccessResponse(data=ReadFolderPolymorphicSerializer(folder).data)

    def destroy(self, request, *args, **kwargs):
        folder = self.get_object()
        
        print(folder.specific)
        # folder.delete()
        return SuccessResponse(status_code=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = WriteFolderPolymorphicSerializer(data=request.data)
        if serializer.is_valid():
            # Create the new folder
            new_folder = serializer.save()
            # Return a response with the created folder's data

            read_serializer = ReadFolderPolymorphicSerializer(new_folder)

            return SuccessResponse(data=read_serializer.data, status_code=status.HTTP_201_CREATED)
        else:
            # If the data is not valid, return a response with the errors
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
