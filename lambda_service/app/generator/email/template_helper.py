from jinja2 import Environment, FileSystemLoader
import os


class Template:
    def __init__(self, order_type=None, template_type=None, context=None):

        if not order_type:
            raise Exception('order_type kwarg is required')
        self.order_type = order_type

        if not template_type:
            raise Exception('type kwarg is required')
        self.template_type = template_type

        if not context:
            raise Exception('type kwarg is required')
        self.context = context

        self.env = Environment(loader=FileSystemLoader(
            '%s/templates/' % os.path.dirname(__file__)))

    def get_template(self, format):
        email_schema = {
            "LPA": {
                "success": "lpa_success_email",
                "lawyer": "certificate_success_lawyer_email",
            },
            "WILL": {
                "success": "will_success_email",
                "lawyer": "witness_success_lawyer_email",
            },
        }

        template_name = f"{email_schema[self.order_type][self.template_type]}.{format}"

        return self.env.get_template(template_name)

    def inject_standard_context(self, context):
        if "unsubscribe_link" not in context.keys():
            context[
                "unsubscribe_link"
            ] = f"https://www.willcraftnow.com/en/unsubscribe/?email={{self.user_email}}"
        return context

    def validate_context(self, context):

        if 'user'not in context.keys():
            raise Exception(
                'user required in context, it should be the userhandle')

        if 'order'not in context.keys():
            raise Exception(
                'order required in context, it should be the order_number')

        return context

    def get_template_context(self):

        self.context = self.validate_context(self.context)

        if "unsubscribe_link" not in self.context.keys():
            self.context[
                "unsubscribe_link"
            ] = f"https://www.willcraftnow.com/en/unsubscribe/?email={{self.user_email}}"

        return self.inject_standard_context(self.context)

    def get_text(self):
        template = self.get_template('txt')
        context = self.get_template_context()
        return template.render(**context)

    def get_html(self):
        context = self.get_template_context()
        template = self.get_template('html')
        return template.render(**context)
