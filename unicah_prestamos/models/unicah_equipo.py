from odoo import fields, models


class UnicahEquipo(models.Model):
    _name = "unicah.equipo"
    _description = "Equipo prestable"

    name = fields.Char(string="Equipo", required=True)
    codigo = fields.Char(string="Código de inventario", required=True)
    categoria = fields.Selection(
        [("laptop", "Laptop"), ("proyector", "Proyector"),
         ("camara", "Cámara"), ("otro", "Otro")],
        string="Categoría", default="otro",
    )
    estado = fields.Selection(
        [("disponible", "Disponible"), ("prestado", "Prestado"),
         ("mantenimiento", "En mantenimiento")],
        string="Estado", default="disponible",
    )
    active = fields.Boolean(default=True)

    _codigo_unico = models.Constraint(
        "UNIQUE(codigo)", "El código de inventario debe ser único."
    )