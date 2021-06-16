def clean_data(data, output="DISPLAY_NAME"):
    if not isinstance(data, dict):
        print("ERROR")

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
                _data[key] = clean_data(value, output=output)
            elif isinstance(value, list):
                _data[key] = [
                    clean_data(listvalue, output=output)
                    if isinstance(listvalue, dict)
                    else listvalue
                    for listvalue in value
                ]
            else:
                _data[key] = value

    return _data
