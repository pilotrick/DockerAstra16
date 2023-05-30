odoo.define('aspl_pos_kitchen_screen.DeliveryTypeBlock', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class DeliveryTypeBlock extends PosComponent {
        get highlight() {
            return this.props.deliveryType.id !== this.props.selectedDelivery.id ? '' : 'highlight';
        }
        get imageUrl() {
            return `/web/image?model=delivery.type&field=image&id=${this.props.deliveryType.id}&unique=1`;
        }
    }
    DeliveryTypeBlock.template = 'DeliveryTypeBlock';

    Registries.Component.add(DeliveryTypeBlock);

    return DeliveryTypeBlock;
});