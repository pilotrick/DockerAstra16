# -*- coding: utf-8 -*-

import json
from odoo.http import Controller, request, route


class SBusController(Controller):

    @route('/pos_sync_session', type="json", auth="public")
    def multi_session_update(self, **args):
        session_id = args['session_id'] if 'session_id' in args else 0
        order = args['order'] if 'order' in args else {}
        res = request.env["pos.sync.session"].browse(int(session_id)).order_operations(order)
        return res
