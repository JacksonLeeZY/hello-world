# -*- coding: utf-8 -*-

from openery import models, fields, api, _, workflow
from openery.exceptions import ValidationError
import datetime as DT
secont modify
# 年结/月结种类定义
class LumiAccountPeriodEndClosingStructure(models.Model):
    _name = "lumi.account.period.end.closing.structure"
    _description = "Lumi Account Period End Closing Structure"

    # 结转顺序
    closing_order = fields.Integer(Stirng='Closing Order', help='Closing Order')
    # 结转名称
    name = fields.Char(String='Name', help='Name')
    # 结转代码
    code = fields.Char(String='Code', help='Code')
    # 结转类型
    type = fields.Selection(selection=[('annual', 'Annual'), ('monthly', 'Monthly')],
                            string='Type', help='Type')
    # 有效
    is_effective = fields.Boolean(string='Effective', help='Effective', default=True)

    _sql_constraints = [
        ('field_unique', 'unique(code)', 'Closing code must be unique per Company!'),
    ]

# 结转模板定义
class LumiAccountPeriodEndClosingSetup(models.Model):
    _name = 'lumi.account.period.end.closing.setup'
    _description = 'Lumi Account Period End Closing Setup'

    # 年结/月结
    annual_or_monthly_id = fields.Selection(selection=[('annual', 'Annual'), ('monthly', 'Monthly')],
                                            string='Annual or Monthly', help='Annual or Monthly')
    # 月结类型
    financial_carry_forward_type = fields.Selection(selection=[('accounting_method', 'Accounting Method'),
                                                               ('table_method', 'Table Method')],
                                                    string='Financial Carry Forward Type',
                                                    help='Financial Carry Forward Type')
    # 结账定义名称
    name = fields.Char(string='Financial Carry Forward Name', help='Financial Carry Forward Name')
    # 有效
    is_effective = fields.Boolean(string='Effective', help='Effective', default=True)
    # 按顺序结账
    is_carry_forward_by_order = fields.Boolean(string='Carry Forward By Order', readonly=True,
                                               help='Carry Forward By Order', default=True)
    # 结转公司
    company_id = fields.Many2one(comodel_name='res.company', string="Company", help="Company",
                                 default=lambda self: self.env.user.company_id, index=True)

    # 结转范围
    setup_lines_ids = fields.One2many(comodel_name='lumi.account.period.end.closing.setup.line',
                                      inverse_name='setup_id',
                                      string='Setup Lines', help='Setup Lines')

    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'The template name cannot be repeated')]

    @api.multi
    def unlink(self):
        count_lines = self.env['lumi.account.run.period.end.closing.line']. \
            search_count([('run_end_closing_id.financial_carry_forward_id', 'in', self.ids)])
        if count_lines > 0:
            raise ValidationError(_("This template is used for monthly carry forward , cannot be deleted."))
        return super(LumiAccountPeriodEndClosingSetup, self).unlink()

   _name = 'lumi.account.period.end.closing.setup.line'



												 
												 
												 
	
	
