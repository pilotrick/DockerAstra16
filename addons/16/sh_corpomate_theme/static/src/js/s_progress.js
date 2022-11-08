odoo.define("sh_corpomate_theme.s_progress", function (require) {
    "use strict";

    var core = require("web.core");
    var _t = core._t;

    var qweb = core.qweb;
    
    $(document).ready(function () {
        //document ready start here.

        /*
         * ----------------------------------------------------------------------------------------------------------------------------------------------
         * PROGRESS BAR
         * ----------------------------------------------------------------------------------------------------------------------------------------------
         */

        var $progress_el_holders = $(".js_cls_render_dynamic_progress_area");

        if ($progress_el_holders && $progress_el_holders.length) {
            // DOM ELEMENTS
            $progress_el_holders.each(function () {
                var percent = $(this).find(".js_cls_s_progress_percent_manual_span").text() || "0%";
                $(this).find(".js_cls_s_progress_percent_auto_style").css("width", percent);
            });
        }

        //document ready ends here.
    });
});
