import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
console.log("OUTSIIIIDEE");
export class GenerateLabelAstraFormController extends FormController {
    setup(){
        super.setup();
        this.orm = useService("orm");
        console.log("TESTIN");
    }

    /**
     * @override
     */
    async beforeExecuteActionButton(clickParams)
    {
        console.log(clickParams)
        // if (clickParams.name === 'export_warrant_payslips') {
        //     if (this.props.saveRecord) {
        //         await this.props.saveRecord(this.model.root, { stayInEdit: true });
        //     } else {
        //         await this.model.root.save({ stayInEdit: true });
        //     }
        //     await this.downloadExportedCSV();
        //     return false;
        // }
        return super.beforeExecuteActionButton(...arguments);
    }

    // async downloadExportedCSV() {
    //     const recordId = this.model.root.data.id;
    //     await download({
    //         url: `/export/warrant_payslips/${recordId}`,
    //         data: {}
    //     });
    //     await this.model.root.load();
    //     this.model.notify();
    //     await this.model.root.switchMode("edit");
    // }
}

registry.category("views").add('print_barcode_labels_zebra', {
    ...formView,
    Controller: GenerateLabelAstraFormController
})

// odoo.define('bi_dynamic_barcode_labels.print_button', function (require)
// {
//     "use strict";
//     var ajax = require("web.ajax");
//     var FormController = require('web.FormController');
//     var BasicController = require('web.BasicController');

//     console.log("OUTSIDE");
//     var FormButton = BasicController.include({

//         _onButtonClicked: function (event)
//         {
//             console.log("MET");
//             if (event.data.attrs.custom === "print_label")
//             {
//                 console.log("METHON");
//                 var products = event.data.record.data.product_barcode_ids.data
//                 products.forEach(element => print_product_label(element.data.product_id.data.id, element.data.company_id, element.data.qty));

//             }

//             if (event.data.attrs.custom === "print_label_product")
//             {
//                 console.log("METHON2");
//                 var products = event.data.record.data.product_barcode_ids.data

//                 products.forEach(element => print_product_label(element.data.product_id.data.id, element.data.company_id.data.id, element.data.qty));
                

//             }


//             function print_product_label(product, company, qty)
//             {
//                 ajax
//                     .jsonRpc("/zebra_label/report", "call", {
//                         'product': product,
//                         'company': company,
//                         'qty': qty })
//                     .then(function (res_data)
//                     {
//                         print_data(res_data);

//                     });
//             }

//             function print_data(data)
//             {
//                 BrowserPrint.getDefaultDevice("printer", function (device)
//                 {
//                     console.log(data.data);
//                     device.send(
                        
//                         data.data,
//                         function (success)
//                         {
//                             device.read(
//                                 function (response) { },
//                                 function (error)
//                                 {
//                                     console.error(error);
//                                 },
//                                 function (error)
//                                 {
//                                     Swal.fire({
//                                         icon: "error",
//                                         title: "Error de Conexion...",
//                                         html: "Verifique la conexion del <strong>Zebra Browser<strong/>",
//                                     });

//                                     console.error(error);
//                                 }
//                             );
//                         },
//                         function (error)
//                         {
//                             Swal.fire({
//                                 icon: "error",
//                                 title: "Error de Conexion...",
//                                 html: "Verifique la conexion del <strong>Zebra Browser<strong/>",
//                             });

//                             console.log("Error de Printer");
//                         }
//                     );
//                 });
//             }
//             this._super(event);
//         },
//     });

//     return FormButton;
// });