from odoo import fields, models, api

class CreateReordering(models.TransientModel):
    _name = 'create.reordering'
    _description = "Create Reordering"
    
    company_ids = fields.Many2many("res.company", string="Company")
    product_category_ids = fields.Many2many("product.category", string="Product Categories")
    product_ids = fields.Many2many("product.product", string="Products")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses")
    period_ids = fields.Many2many("reorder.fiscalperiod", string="Periods")
    operation = fields.Selection([('orderpoint','Reordering Rule'),
                                  ('sales_history','Sales History'),
                                  ('purchase_history', 'Purchase History')],
                                 default="orderpoint", string="Operations")

    orderpoint_operation = fields.Selection([('create_order_point', 'Create Reordering Rule'),
                                  ('update_order_point', 'Update Reordering Rule'),
                                  # ('update_order_point_from_suggestion', 'Update Reordering Rule From Suggestion'),
                                  ],
                                 default="create_order_point", string="Select operation")

    @api.onchange('product_category_ids')
    def onchange_product_category_id(self):
        if self.product_category_ids:
            return {'domain' : { 'product_ids' : [('categ_id','child_of', self.product_category_ids.ids)] }}

    def prepare_orderpoint_domain(self):
        category_ids = company_ids = {}
        # products = []
        # warehouses = []
        # if self.product_category_ids:
        #     products += self.env['product.product'].search([('categ_id','child_of',self.product_category_ids.ids)]).ids
        # elif self.product_ids:
        products = self.product_ids and self.product_ids.ids

        # if self.company_ids:
        #     companies = self.env['res.company'].search([('id', 'child_of', self.company_ids.ids)])
        #     company_ids = set(companies.ids) or {}
        # else:
        #     company_ids = set(self.env.context.get('allowed_company_ids', False) or self.env.user.company_ids.ids) or {}

        warehouses = self.warehouse_ids and self.warehouse_ids.ids or []
        domain = []
        if products:
            domain.append(('product_id', 'in', products))
        if warehouses:
            domain.append(('warehouse_id', 'in', warehouses))

        return domain

    def perform_operation(self):
        operation = self.orderpoint_operation
        if operation == "create_order_point":
            return self.create_reorder_rule()

        elif operation == "update_order_point":
            return self.update_reorder_rule()

        elif operation == "update_order_point_from_suggestion":
            self.update_orderpoint_from_suggestions()

        # elif operation == "export_order_point":
        #     self.export_reorder_rule()
        #
        # elif operation == "import_order_point":
        #     self.import_reorder_rule()

        return True


    def update_orderpoint_from_suggestions(self):
        domain = self.prepare_orderpoint_domain()
        orderpoints = self.env['stock.warehouse.orderpoint'].search(domain)
        for orderpoint in orderpoints:
            orderpoint.update_order_point_data()
        return True

    def update_reorder_rule(self):
        products = self.product_ids and set(self.product_ids.ids) or {}
        warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}
        for period in self.period_ids:
            query = """
                    Select * from update_product_purchase_history('%s','%s','%s','%s','%s')
                """ % (
            products, warehouses, period.fpstartdate.strftime("%Y-%m-%d"),
            period.fpenddate.strftime("%Y-%m-%d"), self.env.user.id)
            self._cr.execute(query)

            query = """
                Select * from update_product_sales_history('{}','%s','{}','%s','%s','%s', '%s')
            """ % (
            products, warehouses, period.fpstartdate.strftime("%Y-%m-%d"),
            period.fpenddate.strftime("%Y-%m-%d"), self.env.user.id)
            self._cr.execute(query)

        domain = self.prepare_orderpoint_domain()
        orderpoints = self.env['stock.warehouse.orderpoint'].search(domain).ids
        for orderpoint_id in orderpoints:
            orderpoint = self.env['stock.warehouse.orderpoint'].browse(orderpoint_id)
            update_ordepoint = orderpoint.product_id and orderpoint.product_id.update_orderpoint or False
            # if update_ordepoint:
            orderpoint.update_product_sales_history()
            orderpoint.update_product_purchase_history()
            orderpoint._calculate_lead_time()
            orderpoint.calculate_sales_average_max()
            orderpoint.onchange_average_sale_calculation_base()
            orderpoint.onchange_safety_stock()
            orderpoint.onchange_avg_sale_lead_time()
            orderpoint.onchange_safety_stock()
            if update_ordepoint:
                orderpoint.update_order_point_data()
        return self.action_orderpoint(orderpoints)

    def create_reorder_rule(self):
        products = self.product_ids and set(self.product_ids.ids) or {}
        warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}
        if not warehouses:
            allowed_company_ids = self.env.context.get('allowed_company_ids', [])
            if allowed_company_ids:
                warehouses = self.env['stock.warehouse'].sudo().search([]).filtered(
                    lambda x: x.company_id.id in allowed_company_ids)
                warehouses = warehouses and set(warehouses.ids) or {}
        if warehouses:
            query = """
            Select * from create_reordering_rule('{}','%s','{}','%s','%s')
            """ % (products, warehouses, self.env.user.id)
            self._cr.execute(query)
            inserted_orderpoints_ids = self._cr.fetchall()
            orderpoints = []
            for record in inserted_orderpoints_ids:
                op_id = record[0]
                orderpoint = self.env['stock.warehouse.orderpoint'].browse(op_id)
                orderpoint.recalculate_data()
                orderpoint.update_order_point_data()
                orderpoints.append(op_id)
            return self.action_orderpoint(orderpoints)
        return True

    def action_orderpoint(self, orderpoints):
        """
        This method will prepare action return.
        :param orderpoints: list of order point ids.
        :return: It will return dictionary of action.
        """
        action = self.env.ref('stock.action_orderpoint').read()[0]
        action['domain'] = [('id','in', orderpoints)]
        return action

    def update_purchase_history(self):
        # category_ids = company_ids = {}
        # if self.product_category_ids:
        #     categories = self.env['product.category'].search([('id', 'child_of', self.product_category_ids.ids)])
        #     category_ids = set(categories.ids) or {}
        products = self.product_ids and set(self.product_ids.ids) or {}

        # if self.company_ids:
        #     companies = self.env['res.company'].search([('id', 'child_of', self.company_ids.ids)])
        #     company_ids = set(companies.ids) or {}
        # else:
        #     company_ids = set(self.env.context.get('allowed_company_ids', False) or self.env.user.company_ids.ids) or {}

        warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}

        for period in self.period_ids:
            query = """
                        Select * from update_product_purchase_history('%s','%s','%s','%s','%s')
                    """ % (
                products, warehouses, period.fpstartdate.strftime("%Y-%m-%d"),
                period.fpenddate.strftime("%Y-%m-%d"), self.env.user.id)
            self._cr.execute(query)
        action = self.env.ref('setu_advance_reordering.product_purchase_history_action').read()[0]
        return action

    def update_sales_history(self):
        category_ids = company_ids = {}
        if self.product_category_ids:
            categories = self.env['product.category'].search([('id', 'child_of', self.product_category_ids.ids)])
            category_ids = set(categories.ids) or {}
        products = self.product_ids and set(self.product_ids.ids) or {}

        if self.company_ids:
            companies = self.env['res.company'].search([('id', 'child_of', self.company_ids.ids)])
            company_ids = set(companies.ids) or {}
        else:
            company_ids = set(self.env.context.get('allowed_company_ids', False) or self.env.user.company_ids.ids) or {}

        warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}

        for period in self.period_ids:
            query = """
                Select * from update_product_sales_history('%s','%s','%s','%s','%s','%s', '%s')
            """ % (
            company_ids, products, category_ids, warehouses, period.fpstartdate.strftime("%Y-%m-%d"),
            period.fpenddate.strftime("%Y-%m-%d"), self.env.user.id)
            self._cr.execute(query)
        action = self.env.ref('setu_advance_reordering.product_sales_history_action').read()[0]
        return action
