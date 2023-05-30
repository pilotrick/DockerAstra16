from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'state' in vals and vals['state'] == 'sale':
            self.send_email_notification()
        return res

    def send_email_notification(self):
        partner_id = self.env['res.users'].browse(self.env.uid).partner_id
        email_from = partner_id.email
        email_to = 'ricardo@ippdr.com'
        subject = 'Notificación de límite de crédito'
        body = f"""
            Hola Ricardo,
            El pedido {self.name} al cliente {self.partner_id} ha alcanzado el estado de límite de crédito por un importe de RD$ {self.amount_total}.
            
            Saludos,
            International Pack & Paper.
            """

        self.message_post(
            body=body,
            subject=subject,
            partner_ids=[partner_id.id],
            email_from=email_from,
            email_to=email_to
        )