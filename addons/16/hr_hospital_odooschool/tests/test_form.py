from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import Form
from odoo.addons.hr_hospital_odooschool.tests.common import HospitalCommon


@tagged('odooschool')
class TestForm(HospitalCommon):

    def test_book_taken_date(self):
        patient_form = Form(self.patient)

        patient_form.doctor_id = self.hospital_trainee.doctor_id
        self.assertEqual(patient_form.taken_date, fields.Date.today())

        patient_form.doctor_id = self.hospital_trainee.doctor_id
        self.assertEqual(patient_form.taken_date, fields.Date.today())
