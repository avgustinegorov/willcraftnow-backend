import string

from html.parser import HTMLParser
import html

from draftjs_exporter.html import HTML
from draftjs_exporter.dom import DOM
from draftjs_exporter.wrapper_state import WrapperState


class DraftToHtmlBlocks(HTML):
    def render(self, block):
        """
        Starts the export process on a given piece of content state.
        """

        wrapper_state = WrapperState(self.block_options, [block])
        entity_map = {}

        return self.render_block(block, entity_map, wrapper_state)


class MyHTMLParser(HTMLParser):
    def __init__(self, block, *args, **kwargs):
        self.block = block
        self.parsed_data = []
        self.styles = []
        self.reconstructed_text = ""
        self.current_position = 0
        self.tag_type = {"b": "BOLD", "em": "ITALIC", "u": "UNDERLINE"}
        super().__init__()

    def feed(self, block):
        from django.utils.safestring import mark_safe

        super().feed(block["text"])
        block["text"] = mark_safe(self.reconstructed_text)
        block["inlineStyleRanges"] = self.styles
        return block

    def handle_starttag(self, tag, attrs):
        self.styles.append(
            {
                "style": self.tag_type[tag],
                "offset": self.current_position,
                "length": None,
            }
        )

    def handle_endtag(self, tag):
        for style in self.styles:
            if style["style"] == self.tag_type[tag] and style["length"] == None:
                style["length"] = self.current_position - style["offset"]

    def handle_data(self, data):
        self.reconstructed_text += data
        self.current_position += len(data)


class DraftJSMixin:
    def generate_draftjs_blocks(self, will_object):
        new_will_object = []
        for block in will_object:
            parser = MyHTMLParser(block)
            updated_block = parser.feed(block)
            new_will_object.append(updated_block)
        return new_will_object

    def generate_html_blocks(self, blocks):
        updated_blocks = []

        for block in blocks:
            rendered_block = DraftToHtmlBlocks().render(block)
            text = html.unescape(DOM.render(rendered_block))
            block["text"] = text
            updated_blocks.append(block)

        return updated_blocks

        return DraftToHtmlBlocks().render(blocks)
