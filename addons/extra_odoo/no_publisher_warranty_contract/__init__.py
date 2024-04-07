from . import models
from odoo.api import Environment, SUPERUSER_ID



def run_pre_init_hook(cr):
    env = Environment(cr, SUPERUSER_ID, {})
    cron = env.ref("mail.ir_cron_module_update_notification", raise_if_not_found=False)
    if cron:
        cron_id = cron.id
        domain = [('model', '=', 'ir.cron'), ('res_id', '=', cron_id),('module', '=', 'mail')]
        model = env['ir.model.data'].search(domain, limit=1)
        if model:
            model.write({'noupdate': False})
            cr.commit()


def run_post_init_hook(cr):
    env = Environment(cr, SUPERUSER_ID, {})
    cron = env.ref("mail.ir_cron_module_update_notification", raise_if_not_found=False)
    if cron:
        cron_id = cron.id
        domain = [('model', '=', 'ir.cron'), ('res_id', '=', cron_id),('module', '=', 'mail')]
        model = env['ir.model.data'].search(domain, limit=1)
        if model:
            model.write({'noupdate': True})
            config = env['ir.config_parameter'].sudo()
            config.set_param('database.expiration_date', '2050-12-30 00:00:00')
            cr.commit()


