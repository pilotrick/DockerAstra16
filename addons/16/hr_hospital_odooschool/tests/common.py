from odoo.tests.common import TransactionCase


class HospitalCommon(TransactionCase):

    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        super(HospitalCommon, self).setUp()
        self.group_hospital_trainee = self.env.ref(
            'hr_hospital_odooschool.group_hospital_trainee')
        self.group_hospital_admin = self.env.ref(
            'hr_hospital_odooschool.group_hospital_admin')

        self.hospital_trainee = self.env['res.users'].create({
            'name': 'Hospital Trainee',
            'login': 'Hospital_trainee',
            'groups_id': [(4, self.env.ref('base.group_user').id),
                          (4, self.group_hospital_trainee.id)],
        })

        self.hospital_admin = self.env['res.users'].create({
            'name': 'Hospital Admin',
            'login': 'Hospital_admin',
            'groups_id': [(4, self.env.ref('base.group_user').id),
                          (4, self.group_hospital_admin.id)],
        })

        self.doctor = self.env['hr.hospital.doctor'].create(
            {
                'name': 'Demo Doctor',
                "sex": "man",
                "phone": "12341278912",
                "specialty": "Therapist"
            }
        )
        self.patient = self.env['hr.hospital.patient'].create(
            {
                'name': 'Demo Patient',
                "sex": "man",
                "phone": "11111278912",
                "specialty": "Psycho"
            }
        )
