from odoo import models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_moves_raw_values(self):
        # Получаем базовый список словарей с компонентами
        moves_values = super()._get_moves_raw_values()
        
        for move_value in moves_values:
            # Проверяем, есть ли ID строки спецификации в данных
            bom_line_id = move_value.get('bom_line_id')
            if bom_line_id:
                bom_line = self.env['mrp.bom.line'].browse(bom_line_id)
                if bom_line.scrap_percentage:
                    # Увеличиваем количество компонента на процент брака
                    move_value['product_uom_qty'] = move_value['product_uom_qty'] * (1 + (bom_line.scrap_percentage / 100.0))
                    
        return moves_values