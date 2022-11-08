/** @odoo-module **/

import { useInputField } from "@web/views/fields/input_field_hook";

const { Component } = owl;

export class SendWAButton extends Component {
    setup() {
        useInputField({ getValue: () =>  this.props.value || '' });
    }
    get formattedPhone() {
        let phone = this.props.value;
        return phone.replace(/\s/g, '');
    }
};
SendWAButton.template = "dx_whatsapp.SendWAButton";
