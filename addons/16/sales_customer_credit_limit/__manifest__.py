# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Customer Credit Limit",
  "summary"              :  """This module adds support for customer credit limit to the Sales Management.""",
  "category"             :  "Sales",
  "version"              :  "1.0.2",
  "sequence"             :  10,
  "author"               :  "Astratech",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Customer-Credit-Limit.html",
  "description"          :  """This module adds support for customer credit limit to the Sales Management & will help you to manage customer credit limit.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=sales_customer_credit_limit",
  "depends"              :  [
                             'hr',
                             'sale_management',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/res_partner_views.xml',
                             'views/sale_views.xml',
                             'wizards/credit_limit_exceed_wizard.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "price"                :  45,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
