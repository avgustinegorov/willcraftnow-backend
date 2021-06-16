from rest_framework import generics, status
from rest_framework.response import Response

from core.permissions import BaseOrderPermission
from utils.views import CustomGetCreateUpdateView, SanitizeOrderPkMixin

from .serializers import *
# Create your views here.


class ListEntitiesView(generics.ListAPIView):
    permission_classes = (BaseOrderPermission,)
    serializer_class = EntitySerializer

    def get_queryset(self):
        """Returns a list of assets belonging to the order
        filtered by user.
        """
        return self.request.user.entities.all()


class ListCreateDoneePowersView(SanitizeOrderPkMixin, generics.ListCreateAPIView):
    serializer_class = DoneePowersSerializer
    permission_classes = (BaseOrderPermission,)

    def get_queryset(self):
        return DoneePowers.objects.filter(donee__order=self.kwargs["order_pk"])


class RetrieveUpdateDestroyDoneePowersView(
    SanitizeOrderPkMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DoneePowersSerializer
    permission_classes = (BaseOrderPermission,)

    def get_object(self):
        return DoneePowers.objects.get(id=self.kwargs["donee_powers_pk"])


class RetrieveUpdateDestroyAppointmentView(
    SanitizeOrderPkMixin, generics.GenericAPIView
):

    serializer_class = AppointmentSerializer
    permission_classes = (BaseOrderPermission,)

    def get_object(self):
        if "person" in self.request.data:
            try:
                return Entity.objects.get(id=self.request.data["person"])
            except Entity.DoesNotExist:  # pragma: no cover
                return None  # pragma: no cover

    def delete(self, request, *args, **kwargs):
        data = request.data.copy()

        person = self.get_object()
        context = self.get_serializer_context()

        serializer = AppointmentSerializer(data=data, context=context)
        if serializer.is_valid():
            serializer.delete(person, serializer.data)
            return Response(serializer.data)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # pragma: no cover

    def post(self, request, **kwargs):
        data = request.data.copy()

        person = self.get_object()
        context = self.get_serializer_context()

        serializer = AppointmentSerializer(
            person, data=data, context=context)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateDestroyPersonalDetailsView(CustomGetCreateUpdateView):

    serializer_class = PersonSerializer
    permission_classes = (BaseOrderPermission,)

    def get_object(self, **kwargs):
        try:
            person_id = self.kwargs.get("person_pk")
            return Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            return None


class RetrieveUpdateDestroyCharityView(CustomGetCreateUpdateView):

    serializer_class = CharitySerializer
    permission_classes = (BaseOrderPermission,)

    def get_object(self, **kwargs):
        try:
            charity_id = self.kwargs.get("charity_pk")
            return Charity.objects.get(id=charity_id)
        except Charity.DoesNotExist:
            return None
