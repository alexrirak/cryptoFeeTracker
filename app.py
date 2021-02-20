from flask import Flask, render_template
import requests
import json

app = Flask(__name__)

API_URL = "https://api.blockcypher.com/v1/"
COINBASE_API = "https://api.coinbase.com/v2/"

COINS = {
    "Bitcoin": "btc",
    "DASH": "dash",
    "Litecoin": "ltc",
    "Ethereum": "eth"
}


@app.route('/')
def main():
    coinData = json.loads(getFees())
    return render_template('main.html', coinData=coinData)

@app.route('/getFees')
def getFees():
    dollarFee = {}
    for name, coin in COINS.items():
        if coin == COINS["Ethereum"]:
            dollarFee[coin] = getEthDollarFee(getBlockChainFeeStats(coin), getCoinbaseSpotPrice(coin))
        else:
            dollarFee[coin] = getDollarFee(getBlockChainFeeStats(coin), getCoinbaseSpotPrice(coin))

    return json.dumps(dollarFee)

def getBlockChainFeeStats(coin):

    response = requests.get(API_URL + coin + "/main")

    if response.status_code == 200:
        parsedResponse = json.loads(response.text)

        if coin == COINS["Ethereum"]:
            result = {}
            result["high"] = parsedResponse['high_gas_price']
            result["medium"] = parsedResponse['medium_gas_price']
            result["low"] = parsedResponse['low_gas_price']
        else:
            result = {}
            result["high"] = parsedResponse['high_fee_per_kb']
            result["medium"] = parsedResponse['medium_fee_per_kb']
            result["low"] = parsedResponse['low_fee_per_kb']

        return result

    return None


def getDollarFee(feeStats, conversionRate, txnSize = 224):
    dollarFees = {}

    dollarFees["high"] = round(getCoinFee(getSatoshiFee(feeStats["high"], txnSize)) * float(conversionRate), 3)
    dollarFees["medium"] = round(getCoinFee(getSatoshiFee(feeStats["medium"], txnSize)) * float(conversionRate), 3)
    dollarFees["low"] = round(getCoinFee(getSatoshiFee(feeStats["low"], txnSize)) * float(conversionRate), 3)

    return dollarFees


def getEthDollarFee(feeStats, dollarConversionRate):
    dollarFees = {}
    weiConversionFactor = 0.000000000000000001
    amountOfGas = 21000
    dollarFees["high"] = round(feeStats["high"] * weiConversionFactor * float(dollarConversionRate) * amountOfGas, 3)
    dollarFees["medium"] = round(feeStats["medium"] * weiConversionFactor * float(dollarConversionRate) * amountOfGas, 3)
    dollarFees["low"] = round(feeStats["low"] * weiConversionFactor * float(dollarConversionRate) * amountOfGas, 3)

    return dollarFees


def getCoinFee(fee):
    # Converts Satoshi to coin
    conversionFactor = 0.00000001
    return fee * conversionFactor


def getSatoshiFee(fee, txnSize):
    # Converts Kb / b
    conversionFactor = 1000
    return fee / conversionFactor * txnSize


def getCoinbaseSpotPrice(coin):
    response = requests.get(COINBASE_API + "prices/" + coin + "-usd/spot")

    if response.status_code == 200:
        return json.loads(response.text)["data"]["amount"]

    return None


if __name__ == '__main__':
    app.run()
