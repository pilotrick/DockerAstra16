/**********************************************************************************
* 
*    Copyright (C) Cetmix OÜ
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU LESSER GENERAL PUBLIC LICENSE for more details.
*
*    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define("prt_report_attachment_preview.action_service", function (require) {
    "use strict";

    const {KeepLast} = require("@web/core/utils/concurrency");
    const {registry} = require("@web/core/registry");
    const {Component, hooks, tags} = owl;
    const {patch} = require("@web/core/utils/patch");
    const {ActionContainer} = require("@web/webclient/actions/action_container");

    const actionRegistry = registry.category("actions");

    var core = require("web.core");
    const _t = core._t;

    function _getReportUrl(action, type) {
        let url = `/report/${type}/${action.report_name}`;
        const actionContext = action.context || {};
        if (action.data && JSON.stringify(action.data) !== "{}") {
            // build a query string with `action.data` (it's the place where reports
            // using a wizard to customize the output traditionally put their options)
            const options = encodeURIComponent(JSON.stringify(action.data));
            const context = encodeURIComponent(JSON.stringify(actionContext));
            url += `?options=${options}&context=${context}`;
        } else {
            if (actionContext.active_ids) {
                url += `/${actionContext.active_ids.join(",")}`;
            }
            if (type === "html") {
                const context = encodeURIComponent(
                    JSON.stringify(env.services.user.context)
                );
                url += `?context=${context}`;
            }
        }
        return url;
    }

    const link =
        '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>';
    const WKHTMLTOPDF_MESSAGES = {
        broken:
            _t(
                "Your installation of Wkhtmltopdf seems to be broken. The report will be shown " +
                    "in html."
            ) + link,
        install:
            _t(
                "Unable to find Wkhtmltopdf on this system. The report will be shown in " +
                    "html."
            ) + link,
        upgrade:
            _t(
                "You should upgrade your version of Wkhtmltopdf to at least 0.12.0 in order to " +
                    "get a correct display of headers and footers as well as support for " +
                    "table-breaking between pages."
            ) + link,
        workers: _t(
            "You need to start Odoo with at least two workers to print a pdf version of " +
                "the reports."
        ),
    };

    let actionCache = {};
    patch(ActionContainer.prototype, "prt_report_attachment_preview.action_service", {
        setup() {
            this._super();
            const env = this.env;
            const keepLast = new KeepLast();
            // only check the wkhtmltopdf state once, so keep the rpc promise
            let wkhtmltopdfStateProm;
            env.bus.on("CLEAR-CACHES", null, () => {
                actionCache = {};
            });
            async function _loadAction(actionRequest, context = {}) {
                if (
                    typeof actionRequest === "string" &&
                    actionRegistry.contains(actionRequest)
                ) {
                    // actionRequest is a key in the actionRegistry
                    return {
                        target: "current",
                        tag: actionRequest,
                        type: "ir.actions.client",
                    };
                }

                if (
                    typeof actionRequest === "string" ||
                    typeof actionRequest === "number"
                ) {
                    // actionRequest is an id or an xmlid
                    const additional_context = {
                        active_id: context.active_id,
                        active_ids: context.active_ids,
                        active_model: context.active_model,
                    };
                    const key = `${JSON.stringify(actionRequest)},${JSON.stringify(
                        additional_context
                    )}`;
                    if (!actionCache[key]) {
                        actionCache[key] = env.services.rpc("/web/action/load", {
                            action_id: actionRequest,
                            additional_context,
                        });
                    }
                    const action = await actionCache[key];
                    if (!action) {
                        return {
                            type: "ir.actions.client",
                            tag: "invalid_action",
                            id: actionRequest,
                        };
                    }
                    return Object.assign({}, action);
                }

                // actionRequest is an object describing the action
                return actionRequest;
            }

            const _super_do_action = env.services.action.doAction;
            env.services.action.doAction = async function (
                actionRequest,
                options = {}
            ) {
                const actionProm = _loadAction(
                    actionRequest,
                    options.additionalContext
                );
                let action = await keepLast.add(actionProm);
                if (
                    action.type === "ir.actions.report" &&
                    action.report_type === "qweb-pdf"
                ) {
                    // check the state of wkhtmltopdf before proceeding
                    if (!wkhtmltopdfStateProm) {
                        wkhtmltopdfStateProm = env.services.rpc(
                            "/report/check_wkhtmltopdf"
                        );
                    }
                    const state = await wkhtmltopdfStateProm;
                    if (state in WKHTMLTOPDF_MESSAGES) {
                        env.services.notification.add(WKHTMLTOPDF_MESSAGES[state], {
                            sticky: true,
                            title: _t("Report"),
                        });
                    }
                    if (state === "upgrade" || state === "ok") {
                        // trigger the download of the PDF report
                        const url = _getReportUrl(action, "pdf");
                        if (!window.open(url)) {
                            // AAB: this check should be done in get_file service directly,
                            // should not be the concern of the caller (and that way, get_file
                            // could return a deferred)
                            var message = _t(
                                "A popup window with your report was blocked. You " +
                                    "may need to change your browser settings to allow " +
                                    "popup windows for this page."
                            );
                            this.doAction({
                                type: "ir.actions.client",
                                tag: "display_notification",
                                params: {
                                    title: _t("Warning"),
                                    message: message,
                                    sticky: true,
                                },
                            });
                        }
                        return Promise.resolve();
                    }
                } else {
                    _super_do_action(actionRequest, options);
                }
            };
        },
    });
});
