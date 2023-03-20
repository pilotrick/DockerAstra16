/** @odoo-module **/
"use strict";

import { registry } from "@web/core/registry";

const { Component } = owl;

export class TableMetricsWidget extends Component {
   setup(){
       super.setup();
       this.props.value = JSON.parse(this.props.value);
   }
}
TableMetricsWidget.template = "lc_detail_and_indicators.table_metrics";

registry.category("fields").add("table_metrics", TableMetricsWidget);