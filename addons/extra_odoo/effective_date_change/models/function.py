from odoo.http import request


def do_query(query, key):
    request.env.cr.execute(query, [key])


def do_update(query, key1, key2):
    request.env.cr.execute(query, [key1, key2])


def concat(pulled_name):
    percent_pulled_name = str(pulled_name + "%")
    return percent_pulled_name


def account_move_concat(year, date):
    stj_account_move_find_sequence = str("STJ" + "/" + year + "/" + date.zfill(2) + "/")
    return stj_account_move_find_sequence


def account_move_new_name(year, date, number):
    stj_account_move_new_name = str("STJ" + "/" + year + "/" + date.zfill(2) + "/" + str(number).zfill(4))
    return stj_account_move_new_name
