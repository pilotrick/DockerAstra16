/** @odoo-module **/

import fieldRegistry from 'web.field_registry';
import { FieldChar } from 'web.basic_fields';
import DynamicPopoverMixin from './list_popover_mixin';
var DynamicCharPopover = FieldChar.extend(DynamicPopoverMixin, {

    init: function ()
    {
        console.log("SS");
        this._super.apply(this, arguments);
        DynamicPopoverMixin.init.call(this, arguments);
    },

    start: function ()
    {
        console.log("SS");
        DynamicPopoverMixin.start.call(this);
        return this._super();
    },

    destroy: function ()
    {
        console.log("SS");
        DynamicPopoverMixin.destroy.call(this);
        this._super.apply(this, arguments);
    },

});
console.log(DynamicCharPopover);
fieldRegistry.add('list.dynamic_popover_char', DynamicCharPopover);

export default DynamicCharPopover;
