from odoo import api, models
from odoo.release import version_info


class PublisherWarrantyContract(models.AbstractModel):
    _inherit = 'publisher_warranty.contract'

    def update_notification(self, cron_mode=True):
        pass
        # return super(PublisherWarrantyContract, self).update_notification(
                # cron_mode=cron_mode)
