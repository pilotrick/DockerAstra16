# @author: Josue Cascante Telegram: @TraderCocoCR
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Tensor - Extra Access Right",
    "version": "15.0.1.2",
    "category": "Tensor",
    "summary": "Tensor - Extra Access Right for certain actions",
    "author": "Tensor-Analitycs",
    "website": "app.tensor-analitycs.pro",
    "license": "AGPL-3",
    "depends": ["point_of_sale", "pos_sale"],
    "data": [
        "security/res_groups.xml",
    ],
    "demo": [
        "demo/res_groups.xml",
    ],
    'assets': {
            'point_of_sale.assets': [
                'pos_access_right/static/src/js/**/*',
                'pos_access_right/static/src/css/pos.css',
                'pos_access_right/static/src/xml/**/*',
            ],
        },
    "installable": True,
}
