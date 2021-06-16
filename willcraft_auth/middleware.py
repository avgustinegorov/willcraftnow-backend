""" Contains all custom middlewares required for WillCraft Authentication """  # pragma: no cover
from django.utils.deprecation import (
    MiddlewareMixin,
)  # For support with django < 2.1  # pragma: no cover

#
# from .models import EmailToken
#
#
# class WillCraftTokenMiddleware(MiddlewareMixin):
# 	""" A Custom <- Request <- Token authentication middleware
# 		that checks for the existence of an X-Token header
# 		token and adds it to the request's session for easy
# 		retrieval in other views
# 	"""
#
# 	def process_request(self, request):
# 		""" Adds the "Token" present in the X-Token
# 			header to the request session
# 		"""
# 		headers = request.META.get("headers", {})
# 		token = headers.get("X-Token", None)
#
# 		if token:
# 			request.session["token"] = EmailToken.objects.filter(token=token).first()
# 			# Turning the token to a json serializable dict so that it can be passed through
# 			# The final process_response middleware
# 			if request.session["token"]:
# 				request.session["token"] = model_to_dict(request.session["token"])
# 		else:
# 			request.session["token"] = None
