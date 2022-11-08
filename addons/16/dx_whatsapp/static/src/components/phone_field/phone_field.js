/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PhoneField } from "@web/views/fields/phone/phone_field";
import { SendWAButton } from '@dx_whatsapp/components/wa_button/wa_button';

patch(PhoneField, "dx_whatsapp.PhoneField", {
    components: {
        ...PhoneField.components,
        SendWAButton
    },
    defaultProps: {
        ...PhoneField.defaultProps,
    },
    props: {
        ...PhoneField.props
    },
    extractProps: ({ attrs }) => {
        return {
            placeholder: attrs.placeholder,
        };
    },
});
