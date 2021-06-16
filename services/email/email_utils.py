import html
import os

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import Context, engines
from django.template.loader import get_template

from services.pdf_gen.invoice_generator import invoice_generator

django_engine = engines["django"]


class SendEmailHelper:
    def __init__(self, *args, order=None, user=None, user_email=None, **kwargs):

        if user:
            self.user_email = user.email
        elif order:
            self.user_email = order.user.email
        else:
            self.user_email = ""

        if order:
            self.order = order
            self.will_pdf, _ = order.get_order_pdf(create=True)
            self.invoice_pdf = invoice_generator(order)
            self.userhandle = order.user.email.split("@")[0]

        self.email_schema = {
            "LPA": {
                "success": "lpa_success_email",
                "lawyer": "certificate_success_lawyer_email",
                "execution": "lpa_execution_letter",
            },
            "WILL": {
                "success": "will_success_email",
                "lawyer": "witness_success_lawyer_email",
                "execution": "will_execution_letter",
            },
        }

    def get_template_name(self, type, format):
        return f"{self.email_schema[self.order.order_type][type]}.{format}"

    def attach_invoice(self):
        # Attaching Invoice
        self.msg.attach(
            "Invoice_" + self.order.order_number,
            self.invoice_pdf.getvalue(),
            "application/pdf",
        )

    def attach_will(self):
        # Attaching Will
        self.msg.attach(
            f"{self.userhandle}.pdf", self.will_pdf.getvalue(), "application/pdf"
        )

    def attach_execution_letter(self):
        # Attaching Execution Letter
        file_name = self.get_template_name("execution", "pdf")
        execution_letter_filepath = os.path.join(
            settings.BASE_DIR, f"templates/email_templates/{file_name}"
        )
        self.msg.attach_file(execution_letter_filepath)

    def attach_lawyer_tncs(self, firm):
        # Attaching tncs
        # with open(firm.tncs_file, mode='rb') as tncs:
        file = firm.tncs_file.read()
        self.msg.attach("terms_and_conditions.pdf", file, "application/pdf")

    def send_email(self):
        sent = self.msg.send(fail_silently=True)
        return sent

    def inject_standard_context(self, context):
        if "unsubscribe_link" not in context.keys():
            context[
                "unsubscribe_link"
            ] = f"https://www.willcraftnow.com/en/unsubscribe/?email={{self.user_email}}"
        return context

    def send_generic_email(
        self,
        htmly=None,
        plaintext=None,
        mail_context={},
        subject=None,
        from_email=None,
        to=None,
        bcc=[],
    ):

        mail_context = self.inject_standard_context(mail_context)

        if not from_email:
            from_email = settings.EMAIL_MAIN
        text_content = plaintext.render(Context(mail_context))
        html_content = htmly.render(Context(mail_context))
        self.msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to], bcc=bcc
        )
        self.msg.attach_alternative(html_content, "text/html")
        sent = self.send_email()
        if sent == 0:
            mail = EmailMessage(
                "[ERROR] Send Generic Email Error",
                "Error when sending email to {}.".format(to),
                settings.EMAIL_MAIN,
                [settings.EMAIL_MAIN],
            )
            mail.send(fail_silently=True)

    def send_success_email(self):
        plaintext = get_template(
            f"email_templates/{self.get_template_name('success', 'txt')}"
        )
        htmly = get_template(
            f"email_templates/{self.get_template_name('success', 'html')}"
        )

        mail_context = {
            "user": self.userhandle,
            "order": self.order.order_number,
        }

        mail_context = self.inject_standard_context(mail_context)

        subject, from_email, to = (
            "[WillCraft] Succcess!",
            settings.EMAIL_MAIN,
            self.order.user.email,
        )
        text_content = plaintext.render(mail_context)
        html_content = htmly.render(mail_context)
        self.msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to], bcc=[settings.EMAIL_MAIN]
        )
        self.msg.attach_alternative(html_content, "text/html")
        self.attach_invoice()
        self.attach_will()
        self.attach_execution_letter()
        sent = self.send_email()
        if sent == 0:
            mail = EmailMessage(
                "[ERROR] Success Email Error",
                "Error when sending email to {}.".format(self.userhandle),
                settings.EMAIL_MAIN,
                [settings.EMAIL_MAIN],
            )
            mail.send(fail_silently=True)

    def send_email_to_admin(self, obj):

        # send email to admin
        plaintext = get_template("email_templates/contact_us.txt")
        htmly = get_template("email_templates/contact_us.html")

        mail_context = {
            "name": obj["name"],
            "email": obj["email"],
            "subject": obj["subject"],
            "message": obj["message"],
        }

        subject, from_email, to = (
            "Enquiry from Website",
            settings.EMAIL_MAIN,
            settings.EMAIL_MAIN,
        )
        text_content = plaintext.render(mail_context)
        html_content = htmly.render(mail_context)
        self.msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to])
        self.msg.attach_alternative(html_content, "text/html")
        sent = self.send_email()
        if sent == 0:
            mail = EmailMessage(
                "[ERROR] Enquiry Email Error",
                "Error when sending email to {}.".format(self.userhandle),
                settings.EMAIL_MAIN,
                [settings.EMAIL_MAIN],
            )
            mail.send(fail_silently=True)

    def send_lawyer_email(self):
        """
        Sending Email to Lawyer
        """

        added_services = self.order.get_added_services()

        if added_services and added_services["services"]:
            # take out this default when done with adjusting lawyer services
            plaintext = get_template(
                f"email_templates/{self.get_template_name('lawyer', 'txt')}"
            )
            htmly = get_template(
                f"email_templates/{self.get_template_name('lawyer', 'html')}"
            )

            firm = added_services["firm"]

            mail_context = {
                "user": self.userhandle,
                "firm": firm.name,
                "order": self.order.order_number,
            }

            mail_context = self.inject_standard_context(mail_context)

            subject, from_email, to = (
                "[WillCraft] Referral to {}".format(firm.name),
                settings.EMAIL_MAIN,
                [firm.email, self.order.user.email],
            )
            text_content = html.unescape(plaintext.render(mail_context))
            html_content = htmly.render(mail_context)
            self.msg = EmailMultiAlternatives(
                subject, text_content, from_email, to, bcc=[
                    settings.EMAIL_MAIN]
            )
            self.msg.attach_alternative(html_content, "text/html")

            self.attach_lawyer_tncs(firm)

            # sending email
            sent = self.send_email()
            if sent == 0:
                mail = EmailMessage(
                    "[ERROR] Referal Error",
                    "Error when referring {} to {}.".format(
                        self.userhandle, firm.name),
                    settings.EMAIL_MAIN,
                    [settings.EMAIL_MAIN],
                )
                mail.send(fail_silently=True)

    def send_admin_email(self, message):
        mail = EmailMessage(
            "[ERROR] Error in Email Sending",
            "Error: {}.".format(message),
            settings.EMAIL_MAIN,
            [settings.EMAIL_MAIN],
        )
        mail.send(fail_silently=True)

    def send_token_email(self, email, token_link):
        plaintext = get_template("email_templates/token_email.txt")
        htmly = get_template("email_templates/token_email.html")

        mail_context = {"link": token_link}

        mail_context = self.inject_standard_context(mail_context)

        subject, from_email, to = "[WillCraft] Guest Login.", settings.EMAIL_MAIN, email
        text_content = plaintext.render(mail_context)
        html_content = htmly.render(mail_context)
        self.msg = EmailMultiAlternatives(
            subject, text_content, from_email, [to], bcc=[settings.EMAIL_MAIN]
        )
        self.msg.attach_alternative(html_content, "text/html")
        sent = self.send_email()
        if sent == 0:
            mail = EmailMessage(
                "[ERROR] Token Email Error",
                "Error when sending email to {}.".format(email),
                settings.EMAIL_MAIN,
                [settings.EMAIL_MAIN],
            )
            mail.send(fail_silently=True)
