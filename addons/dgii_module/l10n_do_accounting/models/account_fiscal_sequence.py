# © 2019 José López <jlopez@indexa.do>
# © 2019 Raul Ovalle <rovalle@guavana.com>

import pytz
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning


def get_l10n_do_datetime():
    """
    Multipurpose Dominican Republic local datetime
    """

    # *-*-*-*-*- Remove this comment *-*-*-*-*-*
    # Because an user can use a distinct timezone,
    # this method ensure that DR localtime stuff like
    # auto expire Fiscal Sequence by its date works,
    # no matter server/client date.

    date_now = datetime.now()
    return pytz.timezone("America/Santo_Domingo").localize(date_now)


class AccountFiscalSequence(models.Model):
    _name = "account.fiscal.sequence"
    _description = "Account Fiscal Sequence"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Authorization number",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    expiration_date = fields.Date(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        default=datetime.strptime(str(int(str(fields.Date.today())[0:4]) + 1) + "-12-31", "%Y-%m-%d").date(),
    )
    fiscal_type_id = fields.Many2one(
        "l10n_latam.document.type", required=True, readonly=True, states={"draft": [("readonly", False)]}, tracking=True,
    )
    type = fields.Char(related="fiscal_type_id.name", store=True,)
    sequence_start = fields.Integer(
        required=True, readonly=True, states={"draft": [("readonly", False)]}, tracking=True, default=1, copy=False,
    )
    sequence_end = fields.Integer(
        required=True, readonly=True, states={"draft": [("readonly", False)]}, tracking=True, default=1, copy=False,
    )
    sequence_remaining = fields.Integer(string="Remaining", compute="_compute_sequence_remaining",)
    sequence_id = fields.Many2one("ir.sequence", string="Internal Sequence", copy=False,)
    warning_gap = fields.Integer(compute="_compute_warning_gap",)
    remaining_percentage = fields.Float(
        default=35,
        required=True,
        help="Fiscal Sequence remaining percentage to reach to start " "warning notifications.",
    )
    number_next_actual = fields.Integer(
        string="Next Number", help="Next number of this sequence", related="sequence_id.number_next_actual",
    )
    next_fiscal_number = fields.Char(compute="_compute_next_fiscal_number",)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("queue", "Queue"),
            ("active", "Active"),
            ("depleted", "Depleted"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        copy=False,
    )
    can_be_queue = fields.Boolean(compute="_compute_can_be_queue",)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.user.company_id,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )

    def _validate_rnc(self):
        if not self.company_id.vat:
            action = self.env.ref("base.action_res_company_form")
            msg = _("Cannot create chart of account until you configure your VAT.")
            raise RedirectWarning(msg, action.id, _("Go to Companies"))



    @api.depends("state")
    def _compute_can_be_queue(self):
        for rec in self:
            rec.can_be_queue = (
                bool(
                    2
                    > self.search_count(
                        [
                            ("state", "in", ("active", "queue")),
                            ("fiscal_type_id", "=", rec.fiscal_type_id.id),
                            ("company_id", "=", rec.company_id.id),
                        ]
                    )
                    > 0
                )
                if rec.state == "draft"
                else False
            )

    @api.depends("remaining_percentage")
    def _compute_warning_gap(self):
        for rec in self:
            rec.warning_gap = (rec.sequence_end - (rec.sequence_start - 1)) * (rec.remaining_percentage / 100)

    @api.depends("sequence_end", "sequence_id.number_next")
    def _compute_sequence_remaining(self):
        for rec in self:
            if rec.sequence_id:
                # Sequence remaining
                rec.sequence_remaining = rec.sequence_end - rec.sequence_id.number_next_actual + 1
            else:
                rec.sequence_remaining = False

    @api.depends("fiscal_type_id.doc_code_prefix", "sequence_id.padding", "sequence_id.number_next_actual")
    def _compute_next_fiscal_number(self):

        for seq in self:
            seq.next_fiscal_number = "%s%s" % (
                seq.fiscal_type_id.doc_code_prefix,
                str(seq.sequence_id.number_next_actual).zfill(seq.sequence_id.padding),
            )

    @api.onchange("fiscal_type_id")
    def _onchange_fiscal_type_id(self):
        """
        Compute draft Fiscal Sequence default sequence_start
        """
        self._validate_rnc()
        if self.fiscal_type_id and self.state == "draft":
            # Last active or depleted Fiscal Sequence
            fs_id = self.search(
                [
                    ("fiscal_type_id", "=", self.fiscal_type_id.id),
                    ("state", "in", ("depleted", "active")),
                    ("company_id", "=", self.company_id.id),
                ],
                order="sequence_end desc",
                limit=1,
            )
            self.sequence_start = fs_id.sequence_end + 1 if fs_id else 1


    @api.constrains("fiscal_type_id", "state")
    def _validate_unique_active_type(self):
        """
        Validate an active sequence type uniqueness
        """
        domain = [
            ("state", "=", "active"),
            ("fiscal_type_id", "=", self.fiscal_type_id.id),
            ("company_id", "=", self.company_id.id),
        ]
        if self.search_count(domain) > 1:
            raise ValidationError(_("Another sequence is active for this type."))


    @api.constrains("sequence_start", "sequence_end", "state", "fiscal_type_id", "company_id")
    def _validate_sequence_range(self):
        for rec in self.filtered(lambda s: s.state != "cancelled"):
            if any([True for value in [rec.sequence_start, rec.sequence_end] if value <= 0]):
                raise ValidationError(_("Sequence values must be greater than zero."))
            if rec.sequence_start >= rec.sequence_end:
                raise ValidationError(_("End sequence must be greater than start sequence."))
            domain = [
                ("sequence_start", ">=", rec.sequence_start),
                ("sequence_end", "<=", rec.sequence_end),
                ("fiscal_type_id", "=", rec.fiscal_type_id.id),
                ("state", "in", ("active", "queue")),
                ("company_id", "=", rec.company_id.id),
            ]
            if rec.search_count(domain) > 1:
                raise ValidationError(_("You cannot use another Fiscal Sequence range."))
        
            ncf = "%s%s" % (
                rec.fiscal_type_id.doc_code_prefix,
                str(rec.sequence_id.number_next_actual).zfill(rec.sequence_id.padding),
            )
            domain = [
                ("l10n_latam_document_number", "=", ncf),
                ("move_type", "in", ["out_invoice", "out_refund"] )
            ]
            result = rec.env["account.move"].search(
                        domain, order="l10n_latam_document_number, id desc", limit=1,
            )
            if result:
                raise ValidationError(_(
                    "NCF *{}* Check the next number, there an Invoice\n\n"
                    "{} with contact {} please check")
                    .format(
                        ncf, 
                        result.name,
                        result.partner_id.name
                        ))

    def unlink(self):
        for rec in self:
            if rec.sequence_id:
                rec.sequence_id.sudo().unlink()
        return super(AccountFiscalSequence, self).unlink()

    def copy(self, default=None):
        if default != "etc":
            raise UserError(_("You cannot duplicate a Fiscal Sequence."))
        return super(AccountFiscalSequence, self).copy(default=default)

    def name_get(self):
        result = []
        for sequence in self:
            result.append((sequence.id, "%s - %s" % (sequence.name, sequence.fiscal_type_id.name)))
        return result

    def action_view_sequence(self):
        self.ensure_one()
        sequence_id = self.sequence_id
        action = self.env.ref("base.ir_sequence_form").read()[0]
        if sequence_id:
            action["views"] = [(self.env.ref("base.sequence_view").id, "form")]
            action["res_id"] = sequence_id.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_confirm(self):
        self.ensure_one()
        self._validate_rnc()
        msg = _(
            "Are you sure want to confirm this Fiscal Sequence? "
            "Once you confirm this Fiscal Sequence cannot be edited."
        )
        action = self.env.ref("l10n_do_accounting.account_fiscal_sequence_validate_wizard_action").read()[0]
        action["context"] = {
            "default_name": msg,
            "default_fiscal_sequence_id": self.id,
            "action": "confirm",
        }
        return action

    def _action_confirm(self):
        for rec in self:

            # Use DR local time
            l10n_do_date = get_l10n_do_datetime().date()

            if l10n_do_date >= rec.expiration_date:
                rec.state = "expired"
            else:
                # Creates a new sequence of this Fiscal Sequence
                if rec.fiscal_type_id.code == "E":
                    padding = 11
                
                else:
                    padding = 8

                sequence_id = self.env["ir.sequence"].create(
                    {
                        "name": _("%s %s Sequence") % (rec.fiscal_type_id.name, rec.name[-9:]),
                        "implementation": "standard",
                        "padding": padding,
                        "number_increment": 1,
                        "number_next_actual": rec.sequence_start,
                        "number_next": rec.sequence_start,
                        "use_date_range": False,
                        "company_id": rec.company_id.id,
                    }
                )
                rec.write({"state": "active", "sequence_id": sequence_id.id})

    def action_cancel(self):
        self.ensure_one()
        msg = _(
            "Are you sure want to cancel this Fiscal Sequence? " "Once you cancel this Fiscal Sequence cannot be used."
        )
        action = self.env.ref("l10n_do_accounting.account_fiscal_sequence_validate_wizard_action").read()[0]
        action["context"] = {
            "default_name": msg,
            "default_fiscal_sequence_id": self.id,
            "action": "cancel",
        }
        return action

    def _action_cancel(self):
        for rec in self:
            rec.state = "cancelled"
            if rec.sequence_id:
                # *-*-*-*-*- Remove this comment *-*-*-*-*-*
                # Preserve internal sequence just for audit purpose.
                rec.sequence_id.active = False

    def action_queue(self):
        for rec in self:
            rec.state = "queue"

    def _expire_sequences(self):
        """
        Function called from ir.cron that check all active sequence
        expiration_date and set state = expired if necessary
        """
        # Use DR local time
        l10n_do_date = get_l10n_do_datetime().date()
        fiscal_sequence_ids = self.search([("state", "=", "active")])

        for seq in fiscal_sequence_ids.filtered(lambda s: l10n_do_date >= s.expiration_date):
            seq.state = "expired"

    def _get_queued_fiscal_sequence(self):
        fiscal_sequence_id = self.search(
            [
                ("state", "=", "queue"),
                ("fiscal_type_id", "=", self.fiscal_type_id.id),
                ("company_id", "=", self.company_id.id),
            ],
            order="sequence_start asc",
            limit=1,
        )
        return fiscal_sequence_id

    def get_fiscal_number(self):

        if self.sequence_remaining > 0:
            sequence_next = self.sequence_id._next()

            # After consume a sequence, evaluate if sequence
            # is depleted and set state to depleted
            if (self.sequence_remaining - 1) < 1:
                self.state = "depleted"
                queue_sequence_id = self._get_queued_fiscal_sequence()
                if queue_sequence_id:
                    queue_sequence_id._action_confirm()

            return "%s%s" % (self.fiscal_type_id.doc_code_prefix, str(sequence_next).zfill(self.sequence_id.padding),)
        else:
            raise ValidationError(_("No Fiscal Sequence available for this type of document."))    
