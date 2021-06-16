from collections import OrderedDict


class BaseUtils(object):

    def clean_data(self, data, output="DISPLAY_NAME"):
        if not isinstance(data, dict):
            raise Exception('input to clean_data should be a dictionary')

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
