/** @odoo-module **/

import { Many2XAutocomplete } from '@web/views/fields/relational_utils';
import { Many2OneField } from '@web/views/fields/many2one/many2one_field';
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

import { usePartnerAutocomplete } from "@l10n_do_accounting/js/partner_autocomplete_core"

export class RNCMany2oneDropdownOption extends Many2XAutocomplete {
    setup() {
        super.setup();
        this.dgii_autocomplete = usePartnerAutocomplete();
    }

    validateSearchTerm(request) {
        return request && request.length > 2;
    }

    get sources() {
        return super.sources.concat(
            {
                options: async (request) => {
                    if (this.validateSearchTerm(request)) {
                        const suggestions = await this.dgii_autocomplete.autocomplete(request);
                        suggestions.forEach((suggestion) => {
                            suggestion.classList = "dgii_autocomplete_dropdown_many2one";
                        });
                        return suggestions;
                    }
                    else {
                        return [];
                    }
                },
                optionTemplate: "l10n_do_accounting.RNCMany2oneDropdownOption",
                placeholder: _t('Buscando RNC...'),
            },
        );
    }

    async onSelect(option, params) {
        if (option.vat) {  // Checks that it is a partner autocomplete option
            const data = await this.dgii_autocomplete.getCreateData(Object.getPrototypeOf(option));
            let context = {
                'default_is_company': true
            };

            if (data.company.vat) {
                context.default_vat = data.company.vat;
            }

            if (data.company.name) {
                context.default_display_name = data.company.name;
                context.default_name = data.company.name;
            }

            return this.openMany2X({ context });
        }
        else {
            return super.onSelect(option, params);
        }
    }

}

export class RNCPartnerAutoCompleteMany2one extends Many2OneField {}

RNCPartnerAutoCompleteMany2one.components = {
    ...Many2OneField.components,
    Many2XAutocomplete: RNCMany2oneDropdownOption,
}

registry.category("fields").add("res_partner_many2one", RNCPartnerAutoCompleteMany2one);
