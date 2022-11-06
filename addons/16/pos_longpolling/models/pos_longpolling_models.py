# -*- coding: utf-8 -*-

import logging
import json
import odoo
from odoo import api, fields, models
from odoo.tools import date_utils


def json_dump(v):
    return json.dumps(v, separators=(',', ':'), default=date_utils.json_default)
_logger = logging.getLogger(__name__)

class ImBus(models.Model):
    _inherit = 'bus.bus'

    @api.model
    def sendmany(self, notifications):
        channels = set()
        values = []
        for channel, message in notifications:
            channels.add(channel)
            values.append({
                "channel": json_dump(channel),
                'message': json_dump([channel,message])
            })
        self.sudo().create(values)
        if channels:
            # We have to wait until the notifications are commited in database.
            # When calling `NOTIFY imbus`, some concurrent threads will be
            # awakened and will fetch the notification in the bus table. If the
            # transaction is not commited yet, there will be nothing to fetch,
            # and the longpolling will return no notification.
            @self.env.cr.postcommit.add
            def notify():
                with odoo.sql_db.db_connect('postgres').cursor() as cr:
                    cr.execute("notify imbus, %s", (json_dump(list(channels)),))

class PosConfig(models.Model):
    _inherit = "pos.config"

    longpolling_max_silence_timeout = fields.Float(
        string="Max Silence timeout (sec)",
        default=60,
        help="Waiting period for any message from poll "
        "(if we have not received a message at this period, "
        "poll will send message ('PING') to check the connection)",
    )
    longpolling_pong_timeout = fields.Float(
        string="Pong timeout (sec)",
        default=10,
        help="Waiting period to receive PONG message after sending PING request."
        "When this timeout occurs, the icon turns "
        "color to red. Once the connection is restored, the icon changes its color "
        "back to green)",
    )
    autostart_longpolling = fields.Boolean(
        "Autostart longpolling",
        default=True,
        help="When switched off longpoling will start only when other module start it",
    )

    def _send_to_channel(self, channel_name, message="PONG"):
        notifications = []
        for ps in self.env["pos.session"].search(
            [("state", "!=", "closed"), ("config_id", "in", self.ids)]
        ):
            channel = ps.config_id._get_full_channel_name(channel_name)
            notifications.append([channel, message])
        if notifications:
            self.env["bus.bus"].sendmany(notifications)
        _logger.debug("POS notifications for %s: %s", self.ids, notifications)
        return 1

    @api.model
    def _send_to_channel_by_id(self, dbname, pos_id, channel_name, message="PONG"):
        channel = self._get_full_channel_name_by_id(dbname, pos_id, channel_name)
        self.env["bus.bus"].sendmany([[channel, message]])
        _logger.debug("POS notifications for %s: %s", pos_id, [[channel, message]])
        return 1

    def _get_full_channel_name(self, channel_name):
        self.ensure_one()
        return self._get_full_channel_name_by_id(self._cr.dbname, self.id, channel_name)

    @api.model
    def _get_full_channel_name_by_id(self, dbname, pos_id, channel_name):
        return '["{}","{}","{}"]'.format(dbname, channel_name, pos_id)

    @api.model
    def send_to_all_poses(self, channel_name, data):
        active_poses = self.search([])
        res = active_poses._send_to_channel(channel_name, data)
        return res
