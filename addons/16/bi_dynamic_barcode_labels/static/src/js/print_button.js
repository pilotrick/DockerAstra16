odoo.define('bi_dynamic_barcode_labels.print_button', function (require)
{
    "use strict";
    var ajax = require("web.ajax");
    var FormController = require('web.FormController');

    FormController.include({
        _onButtonClicked: function (event)
        {
            console.log(event);
            
            if (event.data.attrs.custom === "print_label")
            {

                var products = event.data.record.data.product_barcode_ids.data
                // products.forEach(element => print_product_label(element.data.product_id.data.id, element.data.company_id, element.data.qty));

            }

            if (event.data.attrs.custom === "print_label_product")
            {

                var products = event.data.record.data.product_barcode_ids.data

                // products.forEach(element => print_product_label(element.data.product_id.data.id, element.data.company_id.data.id, element.data.qty));
                

            }


            function print_product_label(product, company, qty)
            {
                ajax
                    .jsonRpc("/zebra_label/report", "call", {
                        'product': product,
                        'company': company,
                        'qty': qty })
                    .then(function (res_data)
                    {
                        print_data(res_data);

                    });
            }

            function print_data(data)
            {
                BrowserPrint.getDefaultDevice("printer", function (device)
                {
                    console.log(data.data);
                    device.send(
                        
                        data.data,
                        function (success)
                        {
                            device.read(
                                function (response) { },
                                function (error)
                                {
                                    console.error(error);
                                },
                                function (error)
                                {
                                    Swal.fire({
                                        icon: "error",
                                        title: "Error de Conexion...",
                                        html: "Verifique la conexion del <strong>Zebra Browser<strong/>",
                                    });

                                    console.error(error);
                                }
                            );
                        },
                        function (error)
                        {
                            Swal.fire({
                                icon: "error",
                                title: "Error de Conexion...",
                                html: "Verifique la conexion del <strong>Zebra Browser<strong/>",
                            });

                            console.log("Error de Printer");
                        }
                    );
                });
            }
            this._super(event);
        },
    });


});