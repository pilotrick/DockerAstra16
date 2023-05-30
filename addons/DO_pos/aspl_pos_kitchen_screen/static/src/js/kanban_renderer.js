/** @odoo-module */
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
const { onPatched, onWillPatch, onWillUpdateProps, useRef, useState } = owl;
import { KanbanModel } from "@web/views/kanban/kanban_model";


patch(KanbanRecord.prototype, "aspl_pos_kitchen_screen/static/src/js/kanban_renderer", {
    async setup() {
        const ORDER_STATE = {'draft': 'PLACED', 'in_progress': 'SHIPPED', 'done': 'DELIVERED'};
        this.orm = useService("orm");
        this.state = useState({lineData: [], delivery_state: 'draft'})
        this.notification = useService("notification");
        await this._super(...arguments);
        const {resModel, model} = this.props.list;
        if(resModel === 'pos.order'){
            this.env.services.bus_service.addEventListener('notification', async ({ detail: notifications }) => {
                for (const { payload, type } of notifications) {
                    if (type === "state.update") {
                        if(this.record && Number(this.record.id.value) == payload.order_id){
                            this.state.delivery_state = payload.state;
                            const {delivery_status, pos_reference} = this.record;
                            this.notification.add(
                                this.env._t(`Order ${ORDER_STATE[delivery_status.raw_value]} Successfully!`),
                                {
                                    title: this.env._t(`${pos_reference.value} Updated!`),
                                    type: "success",
                                },
                            );
                        }
                    }
                    if(type === 'reload.kanban'){
                        await this.loadNewRecords()
                    }
                }
            });
        }
    },
    async loadNewRecords(){
        await this.props.list.load();
        this.props.list.model.notify();
    },
    async createRecordAndWidget(props) {
        const { record } = props;
        await this._super(...arguments);
        const {resModel, model} = this.props.list;
        if(resModel === 'pos.order'){
            for (const fieldName in record.data) {
                const{type, name} = record.fields[fieldName];
                if(fieldName === 'delivery_status'){
                    this.state.delivery_state = record.data[fieldName];
                }
                if(type === 'one2many' && name==='lines') {
                    const value = record.data[fieldName];
                    const data = await this.orm.call("pos.order.line", "read", [value.currentIds, ['full_product_name', 'qty']], {});
                    this.state.lineData = data;
                }
            }
        }
    },
    async changeState(recordId, state){
        const {deliver_by, delivery_service, pos_reference, partner_id} = this.record;
        if ((this.state.delivery_state === state) ||
            (this.state.delivery_state === 'draft' && state==='done') ||
            (state==='in_progress' && this.state.delivery_state === 'done')){
            return;
        }
        await this.orm.call('pos.order', 'change_state', [[Number(recordId)], state]);
    }
});
