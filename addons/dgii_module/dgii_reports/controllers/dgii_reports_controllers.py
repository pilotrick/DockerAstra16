#  Copyright (c) 2018 - Indexa SRL. (https://www.indexa.do) <info@indexa.do>
#  See LICENSE file for full licensing details.

from werkzeug.utils import redirect
from odoo.http import request, Controller, route


class DgiiReportsControllers(Controller):
    @route(["/dgii_reports/<ncf_rnc>"], type="http", auth="user")
    def redirect_link(self, ncf_rnc):

        env = request.env
        base_url = env["ir.config_parameter"].sudo().get_param("web.base.url")

        if str(ncf_rnc)[:1] == "B" or str(ncf_rnc)[:1] == "E":
            invoice_id = env["account.move"].search([("l10n_latam_document_number", "=", ncf_rnc)], limit=1)
            if invoice_id:
                # Get action depending on invoice type
                action_map = {
                    "out_invoice": request.env.ref("account.action_move_out_invoice_type"),
                    "in_invoice": request.env.ref("account.action_move_in_invoice_type"),
                    "out_refund": request.env.ref("account.action_move_out_refund_type"),
                    "in_refund": request.env.ref("account.action_move_in_refund_type"),
                }
                action = action_map[invoice_id.move_type]
                url = "%s/web#id=%s&action=%s&model=account.move&view" "_type=form" % (
                    base_url,
                    invoice_id.id,
                    action.id,
                )

                return redirect(url)  # Returns invoice form view

            return redirect(base_url)

        else:
            partner_id = env["res.partner"].search([("vat", "=", ncf_rnc)], limit=1)
            if partner_id:
                url = "%s/web#id=%s&model=res.partner&view_type=form" % (base_url, partner_id.id)
                return redirect(url)  # Returns partner form view

            return redirect(base_url)
