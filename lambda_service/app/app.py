from generator.generator import Generator
import json
import traceback
# import requests


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        # api-gateway-simple-proxy-for-lambda-input-format
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
        print(event)
        generator = Generator(request_body=json.loads(event['body']))
        generator.run()
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Generation Complete",
                }
            ),
        }
    except Exception as e:
        print("\n".join(traceback.format_exception(
            None, e, e.__traceback__)))
        return {
            "statusCode": 500,
            # "body": json.dumps(
            #     {
            #         "message": e,
            #     }
            # ),
        }
