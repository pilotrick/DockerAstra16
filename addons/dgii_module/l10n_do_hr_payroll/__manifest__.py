# -*- encoding: utf-8 -*-
# © 2019 Jeffry Jesus De La Rosa <jeffryjesus@gmail.com>
# This file is part of Dominincan Republic - HR Payroll

# Dominincan Republic - HR Payroll is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

# Dominincan Republic - HR Payroll is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Dominincan Republic - HR Payroll.  If not,
# see <https://www.gnu.org/licenses/>.

{
    "name": "Dominincan Republic - HR Payroll",
    "summary": u"""
          This Module Will Add Rules, Category and all needed to 
          the Dominican Republic Payroll.
      """,
    "category": "Localization",
    "author": u"""Jeffry Jesus De La Rosa""",
    "depends": ["hr_payroll", "l10n_do", "hr_payroll_account", "contacts", "hr_work_entry_contract", "sh_message"],
    "license": "GPL-3",
    "version": "16.0.0.0.1",
    "description": """
Dominincan Republic - HR Payroll.
=================================

    This Module Will Add:
    - Categories Rules.
    - Structure Rule
    - Salaries Rules.
    - Calculations.
    - Family Dependencies.
    - TSS Reports    
    """,
    "active": True,
    "data": [
        "views/hr_employee_views.xml",
        'security/ir.model.access.csv',
        # "data/l10n_do_hr_payroll_res_partner.xml",
        "data/l10n_do_hr_payroll_rules_categories.xml",
        "data/l10n_do_hr_payroll_salary_rules.xml",
        "data/l10n_do_hr_payroll_structure_labor.xml",
        "data/l10n_do_hr_payroll_rule_input.xml",
        "data/l10n_do_hr_payroll_payslip_config_data.xml",
        "data/l10n_do_hr_payroll_payrolltype.xml",
        # Sequence
        "data/sequence.xml",
        "views/payslip_config_view.xml",
        "views/hr_contract_view.xml",
       # "views/hr_salary_rule_view.xml",
        'views/hr_payslip_run_view.xml',
         'views/working_hours_import_views.xml'
    ],
    "installable": True,
    "auto_install": False,
}
