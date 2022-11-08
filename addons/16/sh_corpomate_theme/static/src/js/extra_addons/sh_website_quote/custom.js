odoo.define("sh_website_quote.sh_contact_us", function (require) {
    const ajax = require("web.ajax");

    $(document).ready(function () {
        $("#sh_wq_website_quote_form").submit(function (e) {
            e.preventDefault();

            var result = ajax
                .jsonRpc("/sh_website_quote/contact_us", "call", {
                    contact_name: $('input[name="contact_name"]').val(),
                    phone: $('input[name="phone"]').val(),
                    email_from: $('input[name="email_from"]').val(),
                    partner_name: $('input[name="partner_name"]').val(),
                    name: $('input[name="name"]').val(),
                    description: $('textarea[name="description"]').val(),
                })
                .then(function (result) {
                    if (result) {
                        $("#sh_wq_website_quote_form").hide();
                        $("#sh_wq_website_quote_thankyou_msg").show();
                        $("#sh_wq_website_quote_thankyou_msg").html('<div class="alert alert-success" style="margin-bottom:0px;"><strong>Your message has been sent successfully. We will get back to you shortly.</strong></div>');
                    } else {
                        $("#sh_wq_website_quote_thankyou_msg").show();
                        $("#sh_wq_website_quote_thankyou_msg").html('<div class="alert alert-danger" style="margin-bottom:0px;"><strong>Failure to request a quote.</strong></div>');
                    }
                });
            return false;
        });

        // Empty form each time when show modal
        $("#sh_wq_website_quote_model").on("show.bs.modal", function () {
            $("#sh_wq_website_quote_form").show();
            $("#sh_wq_website_quote_thankyou_msg").hide();
            $("#sh_wq_website_quote_form")[0].reset();
        });
    });
});
