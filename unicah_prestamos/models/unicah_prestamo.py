from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

DIAS_MAXIMOS = 7


class UnicahPrestamo(models.Model):
    _name = "unicah.prestamo"
    _description = "Préstamo de equipo"
    _order = "fecha_prestamo desc, id desc"

    name = fields.Char(string="Referencia", compute="_compute_name", store=True)
    equipo_id = fields.Many2one("unicah.equipo", string="Equipo", required=True)
    partner_id = fields.Many2one("res.partner", string="Solicitante", required=True)
    fecha_prestamo = fields.Date(string="Fecha de préstamo", required=True,
                                 default=fields.Date.context_today)
    fecha_devolucion_prevista = fields.Date(string="Devolución prevista", required=True)
    fecha_devolucion_real = fields.Date(string="Devolución real", readonly=True, copy=False)
    estado = fields.Selection(
        [("borrador", "Borrador"), ("prestado", "Prestado"), ("devuelto", "Devuelto")],
        string="Estado", default="borrador", readonly=True, copy=False,
    )
    dias_prestamo = fields.Integer(string="Días de préstamo",
                                   compute="_compute_dias_prestamo", store=True)

    @api.depends("equipo_id", "partner_id")
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.equipo_id.name or ''} - {rec.partner_id.name or ''}"

    @api.depends("fecha_prestamo", "fecha_devolucion_prevista")
    def _compute_dias_prestamo(self):
        for rec in self:
            if rec.fecha_prestamo and rec.fecha_devolucion_prevista:
                rec.dias_prestamo = (rec.fecha_devolucion_prevista - rec.fecha_prestamo).days
            else:
                rec.dias_prestamo = 0

    @api.constrains("fecha_prestamo", "fecha_devolucion_prevista")
    def _check_fechas(self):
        for rec in self:
            if rec.fecha_devolucion_prevista < rec.fecha_prestamo:
                raise ValidationError("La devolución no puede ser anterior al préstamo.")
            if rec.dias_prestamo > DIAS_MAXIMOS:
                raise ValidationError(
                    f"Un préstamo no puede superar {DIAS_MAXIMOS} días."
                )

    def action_prestar(self):
        for rec in self:
            if rec.equipo_id.estado != "disponible":
                raise UserError(f"El equipo {rec.equipo_id.name} no está disponible.")
            rec.equipo_id.estado = "prestado"
            rec.estado = "prestado"

    def action_devolver(self):
        for rec in self:
            rec.equipo_id.estado = "disponible"
            rec.estado = "devuelto"
            rec.fecha_devolucion_real = fields.Date.context_today(rec)