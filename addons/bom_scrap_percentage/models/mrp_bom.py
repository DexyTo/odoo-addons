from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    scrap_percentage = fields.Float(
        string='Scrap %',
        digits=(5, 2), # 5 цифр всего, 2 после запятой (макс 999.99%)
        default=0.0,
        help="Процент брака. При создании производственного заказа количество этого компонента будет увеличено на указанный процент."
    )

    @api.constrains('scrap_percentage')
    def _check_scrap_percentage(self):
        for line in self:
            if line.scrap_percentage < 0:
                raise ValidationError("Процент брака не может быть отрицательным числом.")
            if line.scrap_percentage > 100:
                raise ValidationError("Процент брака не может превышать 100%.")