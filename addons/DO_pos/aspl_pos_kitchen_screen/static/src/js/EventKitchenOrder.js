odoo.define('point_of_sale.NumberBuffer', function(require) {
    'use strict';

    const { useListener } = require("@web/core/utils/hooks");
    const { parse } = require('web.field_utils');
    const { _t } = require('web.core');
    const { Gui } = require('point_of_sale.Gui');

    const getDefaultConfig = () => ({
        triggerKitchenData: false,
    });

    const { EventBus, onMounted, onWillUnmount, useComponent, useExternalListener } = owl;

    /**
     * This is a singleton.
     *
     * Only one component can `use` the buffer at a time.
     * This is done by keeping track of each component (and its
     * corresponding state and config) using a stack (bufferHolderStack).
     * The component on top of the stack is the one that currently
     * `holds` the buffer.
     *
     * When the current component is unmounted, the top of the stack
     * is popped and NumberBuffer is set up again for the new component
     * on top of the stack.
     *
     * Usage
     * =====
     * - Activate in the construction of root component. `NumberBuffer.activate()`
     * - Use the buffer in a child component by calling `NumberBuffer.use(<config>)`
     *   in the constructor of the child component.
     * - The component that `uses` the buffer has access to the following instance
     *   methods of the NumberBuffer:
     *   - get()
     *   - set(val)
     *   - reset()
     *   - getFloat()
     *   - capture()
     *
     * Note
     * ====
     * - No need to instantiate as it is a singleton created before exporting in this module.
     *
     * Possible Improvements
     * =====================
     * - Relieve the buffer from responsibility of handling `Enter` and other control keys.
     * - Make the constants (ALLOWED_KEYS, etc.) more configurable.
     * - Write more integration tests. NumberPopup can be used as test component.
     */
    class EventKitchenOrder extends EventBus {
        constructor() {
            super();
        }
        /**
         * @returns {String} value of the buffer, e.g. '-95.79'
         */
        get() {
            return this.state ? this.state.kitchenData : null;
        }
        /**
         * Takes a string that is convertible to float, and set it as
         * value of the buffer. e.g. val = '2.99';
         *
         * @param {String} val
         */
        set(val) {
            this.state.kitchenData = val || [];
            this.trigger('kitchen-order-update', this.state.kitchenData);
        }
        /**
         * Resets the buffer to empty string.
         */
        reset() {
            this.state.kitchenData = [];
            this.trigger('kitchen-order-update', []);
        }
        /**
         * Calling this function, we immediately invoke the `handler` method
         * that handles the contents of the input events buffer (`eventsBuffer`).
         * This is helpful when we don't want to wait for the timeout that
         * is supposed to invoke the handler.
         */
        activate() {
            this.defaultDecimalPoint = _t.database.parameters.decimal_point;
            useExternalListener(window, 'keyup', this._onKeyboardInput.bind(this));
        }
        /**
         * @param {Object} config Use to setup the buffer
         * @param {String|null} config.decimalPoint The decimal character.
         * @param {String|null} config.triggerAtEnter Event triggered when 'Enter' key is pressed.
         * @param {String|null} config.triggerAtEsc Event triggered when 'Esc' key is pressed.
         * @param {String|null} config.triggerAtInput Event triggered for every accepted input.
         * @param {String|null} config.nonKeyboardInputEvent Also listen to a non-keyboard input event
         *      that carries a payload of { key }. The key is checked if it is a valid input. If valid,
         *      the number buffer is modified just as it is modified when a keyboard key is pressed.
         * @param {Boolean} config.useWithBarcode Whether this buffer is used with barcode.
         * @emits config.triggerAtEnter when 'Enter' key is pressed.
         * @emits config.triggerAtEsc when 'Esc' key is pressed.
         * @emits config.triggerAtInput when an input is accepted.
         */
        use(config) {
            this.eventsBuffer = [];
            const currentComponent = useComponent();
            config = Object.assign(getDefaultConfig(), config);
            onMounted(() => {
                this.bufferHolderStack.push({
                    component: currentComponent,
                    state: config.state ? config.state : { buffer: '', toStartOver: false },
                    config,
                });
                this._setUp();
            });
            onWillUnmount(() => {
                this.bufferHolderStack.pop();
                this._setUp();
            });
            // Add listener that accepts non keyboard inputs
            if (typeof config.nonKeyboardInputEvent === 'string') {
                useListener(config.nonKeyboardInputEvent, this._onNonKeyboardInput.bind(this));
            }
        }
        get _currentBufferHolder() {
            return this.bufferHolderStack[this.bufferHolderStack.length - 1];
        }
        _updateBuffer(input) {
            this.trigger('kitchen-order-update', this.state.buffer);
        }
    }

    return new EventKitchenOrder();
});
