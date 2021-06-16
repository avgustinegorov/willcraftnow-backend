from collections import OrderedDict


class BaseParserUtils(object):

    def get_entity_details(self, obj):
        for entity in self.entities:
            if entity['id'] == obj['entity']:
                return entity

    def get_asset_details(self, obj):
        for asset in self.assets:
            if asset['id'] == obj['asset']:
                return asset

    def reduce_allocations(self, allocations, parent_allocation=None):
        reduced_allocations = list(filter(
            lambda allocation: allocation['parent_allocation'] == parent_allocation, allocations))
        for allocation in reduced_allocations:
            allocation['asset'] = self.get_asset_details(allocation)
            allocation['entity'] = self.get_entity_details(allocation)
            allocation['allocations'] = self.reduce_allocations(
                allocations, parent_allocation=allocation['id'])
        return reduced_allocations

    def get_allocation_categories(self, allocations):
        allocation_category = {}
        for allocation in allocations:
            asset_type = allocation['asset']['asset_type']
            if not asset_type in allocation_category:
                allocation_category[asset_type] = []
            allocation_category[asset_type].append(allocation)
        return allocation_category

    def clean_data(self, data, output="DISPLAY_NAME"):
        if not isinstance(data, dict):
            raise Exception('imput to clean_data should be a dictionary')

        _data = {}
        for key, value in data.items():
            if key != "labels" and key != "display_name" and key != "value":
                if isinstance(value, dict) and "value" in value and "display_name" in value:
                    _data[key] = (
                        value["display_name"]
                        if output == "DISPLAY_NAME"
                        else value["value"]
                    )
                elif isinstance(value, dict):
                    _data[key] = self.clean_data(value, output=output)
                elif isinstance(value, list):
                    _data[key] = [
                        self.clean_data(listvalue, output=output)
                        if isinstance(listvalue, dict)
                        else listvalue
                        for listvalue in value
                    ]
                else:
                    _data[key] = value

        return _data

    def roman(self, num):
        """ Converts a Number to a roman numeral """
        roman = OrderedDict()
        roman[1000] = "M"
        roman[900] = "CM"
        roman[500] = "D"
        roman[400] = "CD"
        roman[100] = "C"
        roman[90] = "XC"
        roman[50] = "L"
        roman[40] = "XL"
        roman[10] = "X"
        roman[9] = "IX"
        roman[5] = "V"
        roman[4] = "IV"
        roman[1] = "I"

        def roman_num(num):
            for r in roman.keys():
                x, y = divmod(num, r)
                yield roman[r] * x
                num -= r * x
                if num <= 0:
                    break

        return "".join([a for a in roman_num(num)]).lower()
