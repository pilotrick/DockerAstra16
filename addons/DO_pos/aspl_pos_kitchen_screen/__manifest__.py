# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'POS Kitchen Screen (Community)',
    'version': '1.0.1',
    'category': 'Point of Sale',
    'website': 'http://www.acespritech.com',
    'price': 130.0,
    'currency': 'EUR',
    'summary': "A Screen for kitchen staff in backend",
    'description': """POS kitchen Screen shows orders and their state to Cook and Manager.
                      Mamange Delivery of delivery types orders.
                      No more pos session for the kitchen screen.""",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'depends': ['bus', 'pos_restaurant', 'base', 'pos_epson_printer'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/res_config_setting_view.xml',
        'views/pos_order_view.xml',
        'views/remove_product_reason_view.xml',
        'views/res_users_view.xml',
        'views/delivery_type_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'aspl_pos_kitchen_screen/static/src/css/OrderTypeButton.css',
            'aspl_pos_kitchen_screen/static/src/css/DeliveryTypeButton.css',
            'aspl_pos_kitchen_screen/static/src/js/Chrome.js',
            'aspl_pos_kitchen_screen/static/src/js/models.js',
            'aspl_pos_kitchen_screen/static/src/js/ChromeWidgets/**',
            'aspl_pos_kitchen_screen/static/src/js/Screens/ProductScreen/ControlButtons/SendToKitchenButton.js',
            'aspl_pos_kitchen_screen/static/src/js/Screens/KitchenScreen/KitchenScreen.js',
            'aspl_pos_kitchen_screen/static/src/js/Screens/KitchenScreen/OrderCard.js',
            'aspl_pos_kitchen_screen/static/src/js/Screens/KitchenScreen/OrderCardLine.js',
            'aspl_pos_kitchen_screen/static/src/js/Popups/DeliveryTypeBlock.js',
            'aspl_pos_kitchen_screen/static/src/js/Popups/DeliveryTypePopup.js',
            'aspl_pos_kitchen_screen/static/src/js/Screens/ProductScreen/Orderline.js',
            'aspl_pos_kitchen_screen/static/src/js/Screens/ProductScreen/OrderWidget.js',
            'aspl_pos_kitchen_screen/static/src/js/Screens/SyncPosOrderScreen/SyncOrderScreen.js',
            'aspl_pos_kitchen_screen/static/src/js/Screens/ProductScreen/ProductScreen.js',
            'aspl_pos_kitchen_screen/static/src/scss/pos.css',
            'aspl_pos_kitchen_screen/static/src/xml/Chrome.xml',
            'aspl_pos_kitchen_screen/static/src/xml/ChromeWidgets/KitchenScreenButton.xml',
            'aspl_pos_kitchen_screen/static/src/xml/ChromeWidgets/OrderSyncScreenButton.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/KitchenScreen/KitchenScreen.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/KitchenScreen/OrderCard.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/KitchenScreen/OrderCardLine.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/KitchenScreen/OrderLinePrint.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/KitchenScreen/OrderPrint.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Popups/DeliveryTypeBlock.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Popups/DeliveryTypePopup.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/ProductScreen/ControlButtons/SendToKitchenButton.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/ProductScreen/Orderline.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/ProductScreen/OrderWidget.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/ReceiptScreen/ReceiptScreen.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/SyncPosOrderScreen/SyncOrderScreen.xml',
        ],
        'web.assets_backend': [
            'web_editor/static/lib/html2canvas.js',
            'aspl_pos_kitchen_screen/static/src/js/webclient/webclient.js',
            'aspl_pos_kitchen_screen/static/src/js/MainComponent/MainComponent.js',
            'aspl_pos_kitchen_screen/static/src/js/MainComponent/KitchenScreenNavbar.js',
            'aspl_pos_kitchen_screen/static/src/js/CardOrder/printers.js',
            'aspl_pos_kitchen_screen/static/src/js/CardOrder/devices.js',
            'aspl_pos_kitchen_screen/static/src/js/CardOrder/printerEpson.js',
            'aspl_pos_kitchen_screen/static/src/js/CardOrder/OrderCardBackend.js',
            'aspl_pos_kitchen_screen/static/src/js/CardOrder/OrderCardLineBackend.js',
            'aspl_pos_kitchen_screen/static/src/css/style.css',
            'aspl_pos_kitchen_screen/static/src/scss/kitchen_receipt.css',
            'aspl_pos_kitchen_screen/static/src/xml/WebClient/WebClient.xml',
            'aspl_pos_kitchen_screen/static/src/xml/MainComponent/MainComponent.xml',
            'aspl_pos_kitchen_screen/static/src/xml/MainComponent/KitchenScreenNavbar.xml',
            'aspl_pos_kitchen_screen/static/src/xml/CardOrder/OrderCardBackend.xml',
            'aspl_pos_kitchen_screen/static/src/xml/CardOrder/OrderCardLineBackend.xml',
            'aspl_pos_kitchen_screen/static/src/xml/CardOrder/printImage.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/KitchenScreen/OrderPrint.xml',
            'aspl_pos_kitchen_screen/static/src/xml/Screens/KitchenScreen/OrderLinePrint.xml',
            'aspl_pos_kitchen_screen/static/src/js/kanban_renderer.js',
            'aspl_pos_kitchen_screen/static/src/css/OrderTypeButton.css',
            'aspl_pos_kitchen_screen/static/src/css/delivery_order.css'
        ],
        'web.assets_backend_prod_only': [
            ('replace', 'web/static/src/main.js', 'aspl_pos_kitchen_screen/static/src/main.js'),
        ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
