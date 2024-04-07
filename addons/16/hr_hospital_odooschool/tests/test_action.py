from odoo.addons.hr_hospital_odooschool.tests.common import HospitalCommon
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged('odooschool', 'school',)
class TestAccessRights(HospitalCommon):

    def test_action_take_in(self):
        self.patient.write({'doctor_id': self.hospital_user.doctor_id.id})

        with self.assertRaises(UserError):
            self.patient.with_user(self.hospital_trainee).action_take_in()

        self.patient.with_user(self.hospital_admin).action_take_in()
        self.assertFalse(self.patient.doctor_id)
