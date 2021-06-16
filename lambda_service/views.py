import json
import requests

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.models import WillOrder
from core.serializers import OrderJsonSerializer
from .app.generator.generator import Generator


class TestLambdaView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(WillOrder, pk=kwargs.get('order_pk'))
        serializer_instance = OrderJsonSerializer(
            order, context={"show_display": True})

        body = serializer_instance.json

        headers = {'Content-Type': 'application/json'}

        response = requests.post(
            'https://ry0zlvi1og.execute-api.ap-southeast-1.amazonaws.com/Prod/generator/', data=body, headers=headers)

        print(response.json())

        serializer_instance.save_to_repo()

        return response


class TestView(APIView):  # pragma: no cover
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(WillOrder, pk=kwargs.get('order_pk'))

        serializer_instance = OrderJsonSerializer(
            order, context={"show_display": True})

        body = serializer_instance.json

        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(json.loads(body))

        generator = Generator(
            request_body=json.loads(body), upload=False).run()

        doc_stream = generator.doc_stream()
        invoice_stream = generator.invoice_stream()

        serializer_instance.save_to_repo(
            local=True, doc_pdf=doc_stream, invoice_pdf=invoice_stream)

        response = HttpResponse(doc_stream, content_type="application/pdf")
        response["Content-Disposition"] = 'filename="testhttp.pdf"'
        return response
