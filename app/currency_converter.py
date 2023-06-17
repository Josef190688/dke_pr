class CurrencyConverter:
    rates = {
        'USD': 1.0,
        'EUR': 1.09,
        'CHF': 1.12,
        'SEK': 0.094,
        'JPY': 0.0072,
    }

    @staticmethod
    def convert(amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount

        if from_currency not in CurrencyConverter.rates or to_currency not in CurrencyConverter.rates:
            raise ValueError('Ungültige Währung')

        conversion_rate = CurrencyConverter.rates[to_currency] / CurrencyConverter.rates[from_currency]
        converted_amount = amount * conversion_rate
        return converted_amount

    @staticmethod
    def format(amount, currency):
        formatted_amount = f'{amount:.2f} {currency}'
        return formatted_amount
