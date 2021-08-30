import os

from flask import Flask, jsonify, make_response, request, Response

from .clients import FreeCurrencyAPIClient, ImproperConfiguration

app = Flask(__name__)

app.config["FREE_CURRENCY_API_BASE_URL"] = os.environ.get("FREE_CURRENCY_API_BASE_URL")
app.config["FREE_CURRENCY_API_API_KEY"] = os.environ.get("FREE_CURRENCY_API_API_KEY")

try:
    client = FreeCurrencyAPIClient(
        app.config["FREE_CURRENCY_API_BASE_URL"],
        app.config["FREE_CURRENCY_API_API_KEY"],
    )
except ImproperConfiguration as e:
    app.logger.error(str(e))
    app.logger.error("Please configure the FREE_CURRENCY_API_BASE_URL")
    raise ImproperConfiguration


@app.route("/conversion-rate")
def get_exchange_rate() -> Response:
    """
    - a GET endpoint to get a currency rate
        - Returns the conversion rate from currency1 to currency2 as a floating point number.
        - The rate should be the value of 1 unit of currency1 in currency2.
        - The return value should be a JSON object restating the request parameters and the rate.
    """

    input_currency_type = request.args.get("input_currency_type")
    output_currency_type = request.args.get("output_currency_type")
    conversion_rate = 0

    error_output = {"errors": []}
    if not input_currency_type:
        error_output["errors"].append("specify input_currency_type query parameter")
    if not output_currency_type:
        error_output["errors"].append("specify output_currency_type query parameter")

    try:
        response = client.get_rates(input_currency_type)

        conversion_rate = list(response.json()["data"].items())[0][1][
            output_currency_type
        ]

        app.logger.info(conversion_rate)
    except KeyError:
        error_output["errors"].append(
            f"output_currency_type {output_currency_type} is not a valid currency type"
        )
    except Exception as e:
        app.logger.error(e)
        error_output["errors"].append(str(e))

    output = {
        "params_in": {
            "input_currency_type": input_currency_type,
            "output_currency_type": output_currency_type,
        },
        "conversion_rate": conversion_rate,
    }

    if len(error_output["errors"]) != 0:
        return make_response(jsonify(error_output), 400)
    return jsonify(output)


@app.route("/conversion")
def convert_currency_value() -> Response:
    """
    - a GET endpoint that converts a value in one currency to another
        - returns an amount in one currency, converted to an amount in another currency.
        - The return value should be a JSON object restating the request parameters and the converted amount.
        - All results should be rounded to 2 decimal points.
    """
    input_currency_type = request.args.get("input_currency_type")
    input_value = request.args.get("input_value")
    output_currency_type = request.args.get("output_currency_type")
    converted_value = float()
    conversion_rate = float()

    error_output = {"errors": []}
    if not input_currency_type:
        error_output["errors"].append("specify input_currency_type query parameter")
    if not input_value:
        error_output["errors"].append("specify input_value query parameter")

    try:
        float(input_value)
    except ValueError:
        error_output["errors"].append("input_value must be a decimal value")
    if not output_currency_type:
        error_output["errors"].append("specify output_currency_type query parameter")

    if len(error_output["errors"]) != 0:
        return make_response(jsonify(error_output), 400)

    try:
        response = client.get_rates(input_currency_type)

        conversion_rate = list(response.json()["data"].items())[0][1][
            output_currency_type
        ]
        app.logger.info(f"input value: {input_value}")
        app.logger.info(f"conversion rate: {conversion_rate}")

        converted_value = float(conversion_rate) * float(input_value)

        app.logger.info(conversion_rate)

    except KeyError:
        error_output["errors"].append(
            f"output_currency_type {output_currency_type} is not a valid currency type"
        )
    except Exception as e:
        app.logger.error(e)
        error_output["errors"].append(str(e))

    output = {
        "params_in": {
            "input_currency": input_currency_type,
            "input_value": input_value,
            "output_currency_type": output_currency_type,
        },
        "converted_value": converted_value,
    }
    return jsonify(output)
