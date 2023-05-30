odoo.define('l10n_do_pos.PartnerDetailsEdit', function (require) {
"use strict";
    const { useState } = owl;

    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    const Registries = require("point_of_sale.Registries");

    const PartnerDetailsEditInherit = (PartnerDetailsEdit) =>
        class extends PartnerDetailsEdit {
            constructor() {
                super(...arguments);
                this.state = useState({
                    'l10n_do_dgii_tax_payer_type': this.props.partner.l10n_do_dgii_tax_payer_type,
                });
            }
            saveChanges() {
                this.changes.l10n_do_dgii_tax_payer_type = this.state.l10n_do_dgii_tax_payer_type;
                super.saveChanges();
            }
        };

    Registries.Component.extend(PartnerDetailsEdit, PartnerDetailsEditInherit);
    return PartnerDetailsEdit;
});