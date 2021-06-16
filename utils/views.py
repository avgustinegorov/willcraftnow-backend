from rest_framework import generics, status
from rest_framework.response import Response

from core.models import WillOrder
from core.permissions import BaseOrderPermission

from .query_logger import query_debugger

# Create your views here.


class SanitizeOrderPkMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        order = self.get_order_instance()
        context["order"] = order
        if order:
            context["user"] = order.user
        elif self.request:
            context["user"] = self.request.user
        else:
            context["user"] = None
        context["lang"] = self.request.LANGUAGE_CODE if self.request else None
        context["request"] = self.request
        return context

    def get_order_pk(self):
        order_pk = self.kwargs.get("order_pk", None)
        key = "order_number" if order_pk else None

        if order_pk:
            if isinstance(order_pk, int):
                key = "id"

            if order_pk.isdigit():
                key = "id"
                order_pk = int(order_pk)

        return order_pk, key

    def get_order_instance(self, prefetch_related=[], select_related=[]):
        order_pk, key = self.get_order_pk()

        if not order_pk:
            return None

        if hasattr(self, "order_instance"):
            return self.order_instance

        order_objects = WillOrder.objects

        if len(prefetch_related):
            order_objects = order_objects.prefetch_related(*prefetch_related)

        if len(select_related):
            order_objects = order_objects.select_related(*select_related)

        self.order_instance = order_objects.get(**{key: order_pk})

        return self.order_instance


class CustomGetCreateUpdateView(
    SanitizeOrderPkMixin, generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView
):
    """A Generic view that provides RETRIEVE, CREATE and UPDATE functionality
    for a view linked directly to the `order_pk` url kwarg by a
    OneToOne field

    endpoint: /order/<order_pk>/arrangements/

    get: Return a detailed representation of the WillOrder's Arrangement

    post: Create a new model instance for the given order from the request's body

    put: Update the model instance to the given order's instance
        from the request's body

    patch: Partially update the model instance to the given order's instance
        from the request's body

    Delete: Deletes Instance
    """

    permission_classes = (BaseOrderPermission,)

    def get_object(self):
        """Returns the arrangement belonging to the order identified
        by the `order_pk` url kwarg
        """
        model = self.get_serializer().Meta.model
        order_instance = self.get_order_instance()

        try:
            if model.__name__ != "WillOrder":
                return model.objects.get(order=order_instance)
            else:
                return order_instance  # pragma: no cover
        except model.DoesNotExist:
            return None

    def get_data(self, request):
        # Setting the order pk from the url
        data = request.data.copy()
        data["order"] = self.kwargs.get("order_pk", None)
        return data

    def get_serializer_context(self):
        context = super().get_serializer_context()
        order_pk = self.kwargs.get("order_pk", None)

        if order_pk:
            context["order"] = self.get_order_instance()
            context["lang"] = self.request.LANGUAGE_CODE
        return context

    def create(self, request, *args, **kwargs):
        # Setting the order pk from the url
        data = self.get_data(request)

        # adding additional data if given
        additional_data = kwargs.get("additional_data", {})
        data.update(additional_data)

        # performing usual create mixin functions
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        # Setting the order pk from the url
        data = self.get_data(request)

        # adding additional data if given
        additional_data = kwargs.get("additional_data", {})
        data.update(additional_data)

        # performing usual update mixin functions
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}  # pragma: no cover

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,)
        return Response(serializer.data)
