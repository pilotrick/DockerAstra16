# Part of Odoo. See LICENSE file for full copyright and licensing details.

TEST_URL = 'https://lab.cardnet.com.do'

LIVE_URL = 'https://ecommerce.cardnet.com.do'

IDEMPOTENCY = "/api/payment/idenpotency-keys"
SALE = "/api/payment/sales"
VOID = "/api/payment/voids"
CHECKIN = "/api/payment/checkins"
CHECKOUT = "/api/payment/checkouts"


# Mapping of transaction states to Cardnet {Payment,Setup}Intent statuses.
# See https://Cardnet.com/docs/payments/intents#intent-statuses for the exhaustive list of status.
INTENT_STATUS_MAPPING = {
    'done': ('00'),
    'pending': ('01', '02', '08'),
}

SUPPORTED_CURRENCIES = {
    'DOP': '214',
    'USD': '840',
}