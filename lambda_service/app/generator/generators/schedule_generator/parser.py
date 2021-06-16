import json
import random
import string
from copy import deepcopy
from io import BytesIO

import string

from html.parser import HTMLParser
import html

from draftjs_exporter.html import HTML
from draftjs_exporter.dom import DOM
from draftjs_exporter.wrapper_state import WrapperState
from .parser_utils import ParserUtils
from ..base_parser import BaseParser
from ..mark_safe import mark_safe


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


class ScheduleParser(BaseParser, DraftJSMixin, ParserUtils):
    """A Base Class used to generate will PDFs"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.assetTypes = self.get_asset_categories(self.data["assets"])

        self.main_counter = 0

        self.WillObject = []

    def get_asset_categories(self, assets):
        asset_category = {}
        for asset in assets:
            asset_type = asset['asset_type']
            if not asset_type in asset_category:
                asset_category[asset_type] = []
            asset_category[asset_type].append(asset)
        return asset_category

    def parse_asset_details(self, asset):
        asset_details = asset.pop("asset_details")
        asset_details.update(asset)
        return asset_details

    def object_wrapper(self, text, depth=0, type="ordered-list-item", underline=False):
        key = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(5)
        )
        block_object = {
            "data": {},
            "depth": depth,
            "entityRanges": [],
            "inlineStyleRanges": [],
            "key": key,
            "text": text,
            "type": type,
        }

        self.WillObject.append(block_object)

        return block_object

    def AssetHeader(self, assetName):

        if assetName == "RealEstate":
            assetHeader = "REAL ESTATE"
        elif assetName == "BankAccount":
            assetHeader = "BANK ACCOUNT"
        elif assetName == "Insurance":
            assetHeader = "INSURANCE"
        elif assetName == "Investment":
            assetHeader = "INVESTMENT"
        elif assetName == "Company":
            assetHeader = "COMPANY SHARES"
        elif assetName == "Residual":
            assetHeader = "RESIDUAL"
        else:  # pragma: no cover
            assetHeader = ""  # pragma: no cover

        self.object_wrapper(assetHeader, type="header-four", underline=True)

    def AssetsParagraphs(self):
        for key, value in self.assetTypes.items():
            assetName = key
            assets = value
            if assetName != "Residual":
                self.AssetHeader(assetName)
            for asset in assets:
                if assetName != "Residual":
                    self.object_wrapper(
                        self.AssetDetails(asset, isPartSentence=True), depth=0)

    def parse(self):

        self.AssetsParagraphs()

        return {
            **self.data,
            "blocks": self.generate_draftjs_blocks(self.WillObject)
        }
