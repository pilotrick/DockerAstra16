# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    preview_print = fields.Boolean(
        string="Preview print",
        
    )

    automatic_printing = fields.Boolean(
        string="Automatic printing",
        default=True
    )

    def preview_reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload"
        }

    def preview_print_save(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload_context"
        }

    # Comment this method to can install the module
    # It adds the fields preview_print and automatic_printing to the list of fields that can be read
    # and written by the user
    #It's commented because it causes an internal error and is not mandatory for the operation of the module.
    """ def __init__(self, pool, cr):

        init_res = super(ResUsers, self).__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(
            ["preview_print", "automatic_printing"])
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(
            ["preview_print", "automatic_printing"])

        return init_res """
