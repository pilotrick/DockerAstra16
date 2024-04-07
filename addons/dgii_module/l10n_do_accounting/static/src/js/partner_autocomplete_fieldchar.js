/** @odoo-module **/

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useChildRef } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { CharField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";

import { usePartnerAutocomplete } from "@l10n_do_accounting/js/partner_autocomplete_core"

export class RNCPartnerAutoCompleteCharField extends CharField {
    setup() {
        super.setup();


        this.dgii_autocomplete = usePartnerAutocomplete();

        this.inputRef = useChildRef();
        useInputField({ getValue: () => this.props.value || "", parse: (v) => this.parse(v), ref: this.inputRef});
    }

    async validateSearchTerm(request) {
        if (this.props.name == 'vat')
        {
            return this.dgii_autocomplete.isVATNumber(request);

        }
        else
        {
            return request && request.length > 2;
        }

       
    }

    get sources() {
        return [
            {
                options: async (request) => {
                    if (await this.validateSearchTerm(request)) {
                        const suggestions = await this.dgii_autocomplete.autocomplete(request);
                        suggestions.forEach((suggestion) => {
                            suggestion.classList = "dgii_autocomplete_dropdown_char";
                        });
                        return suggestions;
                    }
                    else {
                        return [];
                    }
                },
                optionTemplate: "l10n_do_accounting.RNCCharFieldDropdownOption",
                placeholder: _t('Buscando RNC...'),
            },
        ];
    }

    async onSelect(option) {
        const data = await this.dgii_autocomplete.getCreateData(Object.getPrototypeOf(option));

        if (data.logo) {
            const logoField = this.props.record.resModel === 'res.partner' ? 'image_1920' : 'logo';
            data.company[logoField] = data.logo;
            console.log(data);
        }

        // Some fields are unnecessary in res.company
        if (this.props.record.resModel === 'res.company') {
            const fields = ['comment', 'child_ids', 'additional_info'];
            fields.forEach((field) => {
                delete data.company[field];
            });
        }

        // Format the many2one fields
        const many2oneFields = ['country_id', 'state_id'];
        many2oneFields.forEach((field) =>
        {
            if (data.company[field]) {
                data.company[field] = [data.company[field].id, data.company[field].display_name];
            }
        });
        this.props.record.update(data.company);
    }
}

RNCPartnerAutoCompleteCharField.template = "l10n_do_accounting.RNCPartnerAutoCompleteCharField";
RNCPartnerAutoCompleteCharField.components = {
    ...CharField.components,
    AutoComplete,
};

registry.category("fields").add("field_dgii_autocomplete", RNCPartnerAutoCompleteCharField);
