from rest_framework import permissions
from .models import WillOrder
from lawyer_services.models import WitnessService, ReviewService


class BaseOrderPermission(permissions.BasePermission):
    """Allows access to an order's detail/update endpoint
    to logged in users if the order doesn't have a user
    or to the order's user if it has one
    """

    def has_permission(self, request, view):
        """Returns True only if the user has a token, or is there is an order_pk in swargs, returns true if the order defined by the "order_pk" url parameter has
        a) The User that is currently authenticated
        b) The token that is currently present in the request's headers
        """
        if request.user and request.user.is_superuser:
            return True
        if request.user and request.user.is_authenticated:
            # if have order_pk check if associated user/token holder has that order, else return true
            if hasattr(view.kwargs, "order_pk"):
                if (
                    view.kwargs["order_pk"] != "undefined"
                    and WillOrder.objects.filter(pk=view.kwargs["order_pk"]).exists()
                ):
                    obj = WillOrder.objects.get(pk=view.kwargs["order_pk"])
                    if obj.user is not None and obj.user == request.user:
                        return True
                    return False
                return False
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """  Return True only if the order's user matches the request's user """

        return self.is_lawyer_or_user(request, view, obj)

    def is_lawyer_or_user(self, request, view, obj):
        """  Return True only if the order's user matches the request's user """

        if request.user and request.user.is_superuser:
            return True

        if type(obj) != WillOrder:
            obj = WillOrder.objects.get(pk=view.kwargs["order_pk"])

        # check authentication first
        if request.user and request.user.is_authenticated:
            if obj.user is not None and obj.user == request.user:
                return True

            if request.user.is_lawyer:
                witness_object = WitnessService.objects.filter(order=obj).latest("id")
                if witness_object.firm in request.user.get_associated_firms:
                    return True

            if request.user.is_lawyer:
                review_object = ReviewService.objects.filter(order=obj).latest("id")
                if review_object.firm in request.user.get_associated_firms:
                    return True

        return False
