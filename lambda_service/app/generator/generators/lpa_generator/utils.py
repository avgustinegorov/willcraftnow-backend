from ..base_utils import BaseUtils


class Utils(BaseUtils):
    def clean_contact_number(self, contact_number):
        if contact_number:
            return contact_number.split(" ")[1].replace("-", "")

    def clean_unit_number(self, unit_number):
        return f"{unit_number:04}" if unit_number else None

    def clean_floor_number(self, floor_number):
        return f"{floor_number:02}" if floor_number else None

    def input_sequential_entry(
        self, template_key, input_string, start_index, max_index
    ):
        print("---" * 10)
        if input_string != None:
            _input_string = str(input_string)
            real_input = ""
            for i in range(len(_input_string)):
                if i < max_index:
                    index = start_index + i
                    key = self.get_key_from_template(
                        template_key, index, start_index)
                    if i == 0:
                        print(key)
                    self.new_schema[key] = _input_string[i]
                    real_input += _input_string[i]
            print(key)
            print("input_string", _input_string)
            print("real_input", real_input)

    def input_checkbox_entry(self, input, index):
        key = self.get_key_from_template("(Check Box_{})", index, index)
        self.new_schema[key] = input

    def get_key_from_template(self, template_key, index, start_index):
        key = template_key.format(index)
        if key in self.all_field_keys:
            return key

        if start_index == 0 and index == 0:
            if "_{})" in template_key:
                template_key = template_key.replace("_{})", ")")
            elif "{})" in template_key:
                template_key = template_key.replace("{})", ")")
        else:
            if "_{})" in template_key:
                template_key = template_key.replace("_{})", "{})")
            elif "{})" in template_key:
                template_key = template_key.replace("{})", "_{})")

        _key = template_key.format(index)
        if _key not in self.all_field_keys:
            print("---" * 20)
            print(f"SCHEMA KEY ERROR {_key}")
            print("---" * 20)
        else:
            print(f"{_key} ====> {key}")

        return _key

    def get_field_value(self, field_name, index, field_type):

        value = field_name

        if field_type == "checkbox":
            try:
                return self.checkbox_schema[field_name]
            except:
                return False
        if field_type == "textfield":
            try:
                return self.textfield_schema[field_name]
            except:
                return ""
        return True
