/** @odoo-module **/

import { startWebClient } from "@web/start";
import { customWebClient } from "./js/webclient/webclient";
/**
 * This file starts the enterprise webclient. In the manifest, it replaces
 * the community main.js to load a different webclient class
 * (WebClientEnterprise instead of WebClient)
 */
startWebClient(customWebClient);