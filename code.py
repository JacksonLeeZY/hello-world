# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, workflow
from odoo.exceptions import ValidationError
import datetime as DT


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

# 结转模板行定义
class LumiAccountPeriodEndClosingSetupLine(models.Model):
    _name = 'lumi.account.period.end.closing.setup.line'
    _description = 'Lumi Account Period End Closing Setup Line'

    setup_id = fields.Many2one(comodel_name='lumi.account.period.end.closing.setup')

    # 年结/月结种类定义
    carry_forward_name_id = fields.Many2one(comodel_name='lumi.account.period.end.closing.structure',
                                            string='Carry Forward Name', help='Carry Forward Name')
    # 结账顺序
    carry_forward_order = fields.Integer(string='Carry Forward Order', help='Carry Forward Order',
                                         related='carry_forward_name_id.closing_order', readonly=True, store=True)
    # 科目自
    account_from = fields.Many2one(comodel_name='account.account', string='Account from', help='Account from')
    # 科目自说明
    account_from_description = fields.Char(string='Account from Description', help='Account from Description',
                                           related='account_from.name', readonly=True)
    # 科目至
    account_to = fields.Many2one(comodel_name='account.account', string='Account to', help='Account to')
    # 科目至说明
    account_to_description = fields.Char(string='Account to Description', help='Account to Description',
                                         related='account_to.name', readonly=True)
    # 结账入科目
    carry_forward_in_account = fields.Many2one(comodel_name='account.account', string='Carry Forward in Account',
                                               help='Carry Forward in Account')
    # 结账入科目说明
    carry_forward_in_description = fields.Char(string='Carry Forward in Description', help='Carry Forward in Description',
                                               related='carry_forward_in_account.name', readonly=True)
    # 是否结转项目
    is_carry_forward_project = fields.Boolean(string='Carry Forward Project', help='Carry Forward Project')

# 运行结转
class LumiAccountRunPeriodEndClosing(models.Model):
    _name = 'lumi.account.run.period.end.closing'
    _description = 'Lumi Account Run Period End Closing'

    # 结转模板
    financial_carry_forward_id = fields.Many2one(comodel_name='lumi.account.period.end.closing.setup',
                                                 string='Financial Carry Forward', help='Financial Carry Forward')
    # 结转模板名称
    name = fields.Char(related='financial_carry_forward_id.name', readonly=True)
    # 结转公司
    company_id = fields.Many2one(comodel_name='res.company', string="Company", help="Company",
                                 related='financial_carry_forward_id.company_id', readonly=True, store=True)
    # 年度
    fiscal_year_id = fields.Many2one(comodel_name='account.fiscalyear', string='Fiscal Year', help='Fiscal Year')
    # 结转期间
    carry_forward_period = fields.Many2one(comodel_name='account.period', store=True,
                                           string='Carry Forward Period', help='Carry Forward Period')
    # 年结/月结
    annual_or_monthly_id = fields.Selection(selection=[('annual', 'Annual'), ('monthly', 'Monthly')],
                                            string='Annual or Monthly', help='Annual or Monthly', readonly=True,
                                            related='financial_carry_forward_id.annual_or_monthly_id')
    # 月结类型
    financial_carry_forward_type = fields.Selection(selection=[('accounting_method', 'Accounting Method'),
                                                               ('table_method', 'Table Method')],
                                                    related='financial_carry_forward_id.financial_carry_forward_type',
                                                    string='Financial Carry Forward Type',
                                                    help='Financial Carry Forward Type', readonly=True)
    # 结转状态
    status = fields.Selection(selection=[('created', 'Created'), ('done', 'Done'), ('canceled', 'Canceled')],
                              string='Status', help='Status', readonly=True, default='created')
    # 结转结果范围
    financial_carry_forward_ids = fields.One2many(comodel_name='lumi.account.run.period.end.closing.line',
                                                  inverse_name='run_end_closing_id',
                                                  string='Financial Carry Forward', help='Financial Carry Forward')

    @api.model
    def create(self, vals):
        res = super(LumiAccountRunPeriodEndClosing, self).create(vals)
        if res['financial_carry_forward_type'] == 'table_method' and res['fiscal_year_id']:
            year_last_month_date_str = str(res['fiscal_year_id'].name) + '-12-01'
            year_last_month_date = DT.datetime.strptime(year_last_month_date_str, "%Y-%m-%d")
            year_last_period = self.env['account.period'].find(year_last_month_date)
            res['carry_forward_period'] = year_last_period and year_last_period.id
        return res


    @api.model
    def monthly_carry_forward(self, run_obj, line, period_id):

        """

        计算每个月的结余
        :param run_obj: 运行对象
        :param line: 对应模板行
        :param period:
        :return: 结余行

        """
        period_obj = self.env['account.period']
        last_day = period_obj.browse(period_id).date_stop
        # 判断是否生成当期的结余凭证
        cfj_id = self.env.ref('lumi_account.carry_forward_journal')
        if self.env['account.move.line'].search_count([('account_id', '=', line.carry_forward_in_account.id),
                                                       ('period_id', '=', period_id),
                                                       ('move_id.journal_id', '=', cfj_id.id)]):
            raise ValidationError(_("There already exist carry forward result."))

        # 判断是否生成上期的结余凭证
        if str(period_obj.browse(period_id).date_start)[5:] != '01-01':
            delta = DT.timedelta(days=-1)
            date = DT.datetime.strptime(self.env['account.period'].browse(period_id).date_start, "%Y-%m-%d")
            pre_date = date + delta
            pre_period_id = self.env['account.period']. \
                search([('company_id', '=', run_obj.company_id.id),
                        ('date_start', '<=', pre_date.strftime('%Y-%m-%d')),
                        ('date_stop', '>=', pre_date.strftime('%Y-%m-%d')),
                        ('special', '=', False)],
                       order='date_start', limit=1).id
            if self.env['lumi.account.run.period.end.closing']. \
                    search_count([('carry_forward_period', '=', pre_period_id),
                                  ('financial_carry_forward_id', '=', run_obj.financial_carry_forward_id.id),
                                  ('status', '=', 'done')]) == 0:
                raise ValidationError \
                    (_("Please carry out pre-period finance carry forward before running this method!"))


        move_lines = []
        account_ids = []
        match_lines = []
        for temp_line in line.setup_id.setup_lines_ids:
            if temp_line.carry_forward_in_account.id == line.carry_forward_in_account.id:
                match_lines.append(temp_line)
        # 合并相同结转分录行
        for second_line in match_lines:

            account_ids += self.env['account.account'].search([('code', '>', second_line.account_from.code),
                                                               ('code', '<', second_line.account_to.code)]).ids
            account_ids += self.env['account.account'].search([('id', 'child_of', second_line.account_from.id)]).ids
            account_ids += self.env['account.account'].search([('id', 'child_of', second_line.account_to.id)]).ids
        account_ids = list(set(account_ids))

        sql = """
                            SELECT COUNT(*) AS num,
                                SUM(coalesce(debit, 0)) AS debit,
                                SUM(coalesce(credit, 0)) AS credit
                              FROM account_move_line
                            WHERE account_id in %s and period_id = %s
                        """

        self.env.cr.execute(sql, [tuple(account_ids), period_id])
        sql_value = self.env.cr.dictfetchall()

        if line.is_carry_forward_project or 1:  # 如果科目启动强制核算则必须启动结转项目，否则生成凭证会有错，所以要考虑将结转项目设为自动给值
            sql = """
                                SELECT account_id, analytics_id,
                                SUM(coalesce(debit, 0)) AS debit, SUM(coalesce(credit, 0)) AS credit
                                  FROM account_move_line
                                WHERE account_id in %s and period_id = %s
                                  GROUP BY account_id, analytics_id
                                """
        else:
            sql = """
                                SELECT account_id,
                                SUM(coalesce(debit, 0)) AS debit, SUM(coalesce(credit, 0)) AS credit
                                  FROM account_move_line
                                WHERE account_id in %s and period_id = %s
                                  GROUP BY account_id
                                """

        self.env.cr.execute(sql, [tuple(account_ids), period_id])
        values = self.env.cr.dictfetchall()
        analytics_ids = []
        for value in values:
            temp_analytic = value.get('analytics_id', False)
            if temp_analytic:
                analytics_ids.append(temp_analytic)

        if analytics_ids and line.carry_forward_in_account.force_analytic \
                and line.carry_forward_in_account.analytic_plan_id:
            for analytics_id in list(set(analytics_ids)):
                sum_debit = 0
                for value in values:
                    if value.get('analytics_id', False) == analytics_id:
                        debit_credit = value['debit'] - value['credit']
                        sum_debit += debit_credit
                        l_line = {
                            'name': period_obj.browse(period_id).name + ' ' + run_obj.financial_carry_forward_id.name,
                            'account_id': value['account_id'],
                            'debit': -debit_credit if debit_credit < 0 else 0,
                            'credit': debit_credit if debit_credit > 0 else 0,
                            'analytics_id': analytics_id,
                        }
                        move_lines.append([0, 0, l_line])

                move_lines.append([0, 0, {
                    'name': period_obj.browse(period_id).name + ' ' + run_obj.financial_carry_forward_id.name,
                    'account_id': line.carry_forward_in_account.id,
                    'debit': sum_debit if sum_debit> 0 else 0,
                    'credit': -sum_debit if sum_debit < 0 else 0,
                    'analytics_id': analytics_id,
                }])
        else:
            sum_debit = 0
            for value in values:
                debit_credit = value['debit'] - value['credit']
                sum_debit += debit_credit
                l_line = {
                    'name': period_obj.browse(period_id).name + ' ' + run_obj.financial_carry_forward_id.name,
                    'account_id': value['account_id'],
                    'debit': -debit_credit if debit_credit < 0 else 0,
                    'credit': debit_credit if debit_credit > 0 else 0,
                    'analytics_id': value.get('analytics_id', False),
                }
                move_lines.append([0, 0, l_line])

            move_lines.append([0, 0, {
                'name': period_obj.browse(period_id).name + ' ' + run_obj.financial_carry_forward_id.name,
                'account_id': line.carry_forward_in_account.id,
                'debit': sum_debit if sum_debit > 0 else 0,
                'credit': -sum_debit if sum_debit < 0 else 0,
                'analytics_id': False,
            }])

        vals_move = {
            'journal_id': self.env.ref('lumi_account.carry_forward_journal').id,
            'period_id': period_id,
            'date': last_day,
            'company_id': run_obj.company_id.id,
            'abstract': period_obj.browse(period_id).name + ' ' + run_obj.financial_carry_forward_id.name,
            'line_id': move_lines
        }

        if len(move_lines) > 1:
            move_id = self.env['account.move'].create(vals_move)
        else:
            move_id = False

        carry_forward_values = {
            'carry_forward_name_id': line.carry_forward_name_id.id,
            'carry_forward_period_id': period_id,
            'carry_forward_account_lines': sql_value[0]['num'],
            'carry_forward_debit_amount': sql_value[0]['debit'],
            'carry_forward_credit_amount': sql_value[0]['credit'],
            'carry_forward_account_move': move_id.id if move_id else False,
            'run_end_closing_id': run_obj.id
        }
        self.env['lumi.account.run.period.end.closing.line'].create(carry_forward_values)

    @api.one
    def run_financial_carry_forward(self):
        last_day = self.carry_forward_period.date_stop
        # 月结-账结
        if self.annual_or_monthly_id == 'monthly' and self.financial_carry_forward_type == 'accounting_method':
            line_ids = self.financial_carry_forward_id.setup_lines_ids.ids
            carry_forward_accounts = []
            for line in self.env['lumi.account.period.end.closing.setup.line']. \
                    search([('id', 'in', line_ids)], order='carry_forward_order'):
                if line.carry_forward_in_account.id in carry_forward_accounts:
                    continue
                else:
                    carry_forward_accounts.append(line.carry_forward_in_account.id)
                self.monthly_carry_forward(self, line, self.carry_forward_period.id)

            self.status = 'done'


        # 月结-表结
        elif self.annual_or_monthly_id == 'monthly' and self.financial_carry_forward_type == 'table_method':
            period_obj = self.env['account.period']

            year_first_month_date_str = str(self.fiscal_year_id.name) + '-01-01'
            year_last_month_date_str = str(self.fiscal_year_id.name) + '-12-01'
            year_first_month_date = DT.datetime.strptime(year_first_month_date_str, "%Y-%m-%d")
            year_last_month_date = DT.datetime.strptime(year_last_month_date_str, "%Y-%m-%d")
            year_first_period = period_obj.find(year_first_month_date)
            year_last_period = period_obj.find(year_last_month_date)

            if year_last_period.date_start >= fields.Datetime.now():
                raise ValidationError(_("Table method can not be implemented before december."))
            period_ids = self.env['account.period'].search([('date_start', '>=', year_first_period.date_start),
                                                            ('date_start', '<=', year_last_period.date_stop),
                                                            ('company_id', '=',
                                                             self.financial_carry_forward_id.company_id.id),
                                                            ('special', '=', False)], order='date_start').ids

            line_ids = self.financial_carry_forward_id.setup_lines_ids.ids
            carry_forward_accounts = []
            cfj_id = self.env.ref('lumi_account.carry_forward_journal')
            for line in self.env['lumi.account.period.end.closing.setup.line']. \
                    search([('id', 'in', line_ids)], order='carry_forward_order'):

                if line.carry_forward_in_account.id in carry_forward_accounts:
                    continue
                else:
                    carry_forward_accounts.append(line.carry_forward_in_account.id)

                if self.env['account.move.line'].search_count([('account_id', '=', line.carry_forward_in_account.id),
                                                               ('period_id', '=', year_last_period.id),
                                                               ('move_id.journal_id', '=', cfj_id.id)]):
                    raise ValidationError(_("There already exist carry forward result."))

                move_lines = []
                account_ids = []
                match_lines = []
                for temp_line in line.setup_id.setup_lines_ids:
                    if temp_line.carry_forward_in_account.id == line.carry_forward_in_account.id:
                        match_lines.append(temp_line)
                # 合并相同结转分录行
                for second_line in match_lines:
                    account_ids += self.env['account.account']. \
                        search([('code', '>', second_line.account_from.code),
                                ('code', '<', second_line.account_to.code)]).ids
                    account_ids += self.env['account.account'].search(
                        [('id', 'child_of', second_line.account_from.id)]).ids
                    account_ids += self.env['account.account'].search(
                        [('id', 'child_of', second_line.account_to.id)]).ids
                account_ids = list(set(account_ids))

                sql = """
                        SELECT COUNT(*) AS num,
                            SUM(coalesce(debit, 0)) AS debit,
                            SUM(coalesce(credit, 0)) AS credit
                        FROM account_move_line
                        WHERE account_id in %s and period_id in %s
                                        """

                self.env.cr.execute(sql, [tuple(account_ids), tuple(period_ids)])
                sql_value = self.env.cr.dictfetchall()

                if line.is_carry_forward_project or 1:
                    sql = """
                            SELECT account_id, analytics_id,
                                SUM(coalesce(debit, 0)) AS debit, SUM(coalesce(credit, 0)) AS credit
                            FROM account_move_line
                            WHERE account_id in %s and period_id in %s
                                GROUP BY account_id, analytics_id
                                                """
                else:
                    sql = """
                            SELECT account_id,
                                SUM(coalesce(debit, 0)) AS debit, SUM(coalesce(credit, 0)) AS credit
                            FROM account_move_line
                            WHERE aml.account_id in %s and aml.period_id in %s
                                GROUP BY account_id
                                                """

                self.env.cr.execute(sql, [tuple(account_ids), tuple(period_ids)])
                values = self.env.cr.dictfetchall()

                analytics_ids = []
                for value in values:
                    temp_analytic = value.get('analytics_id', False)
                    if temp_analytic:
                        analytics_ids.append(temp_analytic)

                if analytics_ids and line.carry_forward_in_account.force_analytic \
                        and line.carry_forward_in_account.analytic_plan_id:
                    for analytics_id in list(set(analytics_ids)):
                        sum_debit = 0
                        for value in values:
                            if value.get('analytics_id', False) == analytics_id:
                                debit_credit = value['debit'] - value['credit']
                                sum_debit += debit_credit
                                l_line = {
                                    'name': self.fiscal_year_id.name + _('year') + self.financial_carry_forward_id.name,
                                    'account_id': value['account_id'],
                                    'debit': -debit_credit if debit_credit < 0 else 0,
                                    'credit': debit_credit if debit_credit > 0 else 0,
                                    'analytics_id': analytics_id,
                                }
                                move_lines.append([0, 0, l_line])

                        move_lines.append([0, 0, {
                            'name': year_last_period.name + ' ' + self.financial_carry_forward_id.name,
                            'account_id': line.carry_forward_in_account.id,
                            'debit': sum_debit if sum_debit > 0 else 0,
                            'credit': -sum_debit if sum_debit < 0 else 0,
                            'analytics_id': analytics_id,
                        }])
                else:
                    sum_debit = 0
                    for value in values:
                        debit_credit = value['debit'] - value['credit']
                        sum_debit += debit_credit
                        l_line = {
                            'name': self.fiscal_year_id.name + _('year') + self.financial_carry_forward_id.name,
                            'account_id': value['account_id'],
                            'debit': -debit_credit if debit_credit < 0 else 0,
                            'credit': debit_credit if debit_credit > 0 else 0,
                            'analytics_id': value.get('analytics_id', False),
                        }
                        move_lines.append([0, 0, l_line])

                    move_lines.append([0, 0, {
                        'name': year_last_period.name + ' ' + self.financial_carry_forward_id.name,
                        'account_id': line.carry_forward_in_account.id,
                        'debit': sum_debit if sum_debit > 0 else 0,
                        'credit': -sum_debit if sum_debit < 0 else 0,
                        'analytics_id': False,
                    }])

                vals_move = {
                    'journal_id': self.env.ref('lumi_account.carry_forward_journal').id,
                    'period_id': year_last_period.id,
                    'date': last_day,
                    'company_id': self.company_id.id,
                    'abstract': year_last_period.name + ' ' + self.financial_carry_forward_id.name,
                    'line_id': move_lines
                }

                if len(move_lines) > 1:
                    move_id = self.env['account.move'].create(vals_move)
                else:
                    move_id = False

                carry_forward_values = {
                    'carry_forward_name_id': line.carry_forward_name_id.id,
                    'carry_forward_period_id': year_last_period.id,
                    'carry_forward_account_lines': sql_value[0]['num'],
                    'carry_forward_debit_amount': sql_value[0]['debit'],
                    'carry_forward_credit_amount': sql_value[0]['credit'],
                    'carry_forward_account_move': move_id.id if move_id else False,
                    'run_end_closing_id': self.id
                }
                self.env['lumi.account.run.period.end.closing.line'].create(carry_forward_values)

            self.status = 'done'

        # 年结
        elif self.annual_or_monthly_id == 'annual':
            # 获取当前日期本年最后一天
            today = datetime.date.today()
            last_year_day = datetime.date(today.year, 12, 31)
            period_obj = self.env['account.period']
            year_first_month_date_str = str(self.fiscal_year_id.name) + '-01-01'
            year_last_month_date_str = str(self.fiscal_year_id.name) + '-12-01'
            year_first_month_date = DT.datetime.strptime(year_first_month_date_str, "%Y-%m-%d")
            year_last_month_date = DT.datetime.strptime(year_last_month_date_str, "%Y-%m-%d")
            year_first_period = period_obj.find(year_first_month_date)
            year_last_period = period_obj.find(year_last_month_date)

            # 第十三个期间
            target_period = period_obj.search([('date_start', '>=', year_last_period.date_stop),
                                               ('date_stop', '<=', year_last_period.date_stop),
                                               ('company_id', '=', self.financial_carry_forward_id.company_id.id)])

            if target_period:
                target_period = target_period[0].id
            else:
                target_period = year_last_period.id

            period_ids = self.env['account.period'].search([('date_start', '>=', year_first_period.date_start),
                                                            ('date_start', '<=', year_last_period.date_stop),
                                                            ('company_id', '=',
                                                             self.financial_carry_forward_id.company_id.id),
                                                            ('special', '=', False)], order='date_start').ids

            cfj_id = self.env.ref('lumi_account.carry_forward_journal')
            line_ids = self.financial_carry_forward_id.setup_lines_ids.ids
            carry_forward_accounts = []
            for line in self.env['lumi.account.period.end.closing.setup.line'].search([('id', 'in', line_ids)],
                                                                                      order='carry_forward_order'):

                if line.carry_forward_in_account.id in carry_forward_accounts:
                    continue
                else:
                    carry_forward_accounts.append(line.carry_forward_in_account.id)

                try:
                    # 是否存在本年12月的 月结执行记录
                    if not self.env['lumi.account.run.period.end.closing.line']. \
                            search_count([('run_end_closing_id.carry_forward_period', '=', year_last_period.id)]):
                        raise ValidationError(_(
                            "The december monthly finance carry forward should be done before implementing year finance carry forward."))

                    if self.env['account.move.line'].search_count(
                            [('account_id', '=', line.carry_forward_in_account.id),
                             ('period_id', '=', target_period),
                             ('move_id.journal_id', '=', cfj_id.id)]):
                        raise ValidationError(_("There already exist carry forward result."))

                    move_lines = []
                    account_ids = []
                    match_lines = []
                    for temp_line in line.setup_id.setup_lines_ids:
                        if temp_line.carry_forward_in_account.id == line.carry_forward_in_account.id:
                            match_lines.append(temp_line)
                    # 合并相同结转分录行
                    for second_line in match_lines:
                        account_ids += self.env['account.account']. \
                            search([('code', '>', second_line.account_from.code),
                                    ('code', '<', second_line.account_to.code)]).ids
                        account_ids += self.env['account.account'].search(
                            [('id', 'child_of', second_line.account_from.id)]).ids
                        account_ids += self.env['account.account'].search(
                            [('id', 'child_of', second_line.account_to.id)]).ids
                    account_ids = list(set(account_ids))

                    sql = """
                            SELECT COUNT(*) AS num,
                                SUM(coalesce(debit, 0)) AS debit,
                                SUM(coalesce(credit, 0)) AS credit
                            FROM account_move_line
                            WHERE account_id in %s and period_id in %s
                                            """

                    self.env.cr.execute(sql, [tuple(account_ids), tuple(period_ids)])
                    sql_value = self.env.cr.dictfetchall()

                    if line.is_carry_forward_project or 1:
                        sql = """
                                SELECT account_id, analytics_id,
                                    SUM(coalesce(debit, 0)) AS debit, SUM(coalesce(credit, 0)) AS credit
                                FROM account_move_line
                                WHERE account_id in %s and period_id in %s
                                    GROUP BY account_id, analytics_id
                                                    """
                    else:
                        sql = """
                                SELECT account_id,
                                    SUM(coalesce(debit, 0)) AS debit, SUM(coalesce(credit, 0)) AS credit
                                FROM account_move_line
                                WHERE aml.account_id in %s and aml.period_id in %s
                                    GROUP BY account_id
                                                    """

                    self.env.cr.execute(sql, [tuple(account_ids), tuple(period_ids)])
                    values = self.env.cr.dictfetchall()

                    analytics_ids = []
                    for value in values:
                        temp_analytic = value.get('analytics_id', False)
                        if temp_analytic:
                            analytics_ids.append(temp_analytic)

                    if analytics_ids and line.carry_forward_in_account.force_analytic \
                            and line.carry_forward_in_account.analytic_plan_id:
                        for analytics_id in list(set(analytics_ids)):
                            sum_debit = 0
                            for value in values:
                                if value.get('analytics_id', False) == analytics_id:
                                    debit_credit = value['debit'] - value['credit']
                                    sum_debit += debit_credit
                                    l_line = {
                                        'name': self.fiscal_year_id.name + _(
                                            'year') + self.financial_carry_forward_id.name,
                                        'account_id': value['account_id'],
                                        'debit': -debit_credit if debit_credit < 0 else 0,
                                        'credit': debit_credit if debit_credit > 0 else 0,
                                        'analytics_id': analytics_id,
                                    }
                                    move_lines.append([0, 0, l_line])

                            move_lines.append([0, 0, {
                                'name': self.fiscal_year_id.name + _('year') + self.financial_carry_forward_id.name,
                                'account_id': line.carry_forward_in_account.id,
                                'debit': sum_debit if sum_debit > 0 else 0,
                                'credit': -sum_debit if sum_debit < 0 else 0,
                                'analytics_id': analytics_id,
                            }])
                    else:
                        sum_debit = 0
                        for value in values:
                            debit_credit = value['debit'] - value['credit']
                            sum_debit += debit_credit
                            l_line = {
                                'name': self.fiscal_year_id.name + _('year') + self.financial_carry_forward_id.name,
                                'account_id': value['account_id'],
                                'debit': -debit_credit if debit_credit < 0 else 0,
                                'credit': debit_credit if debit_credit > 0 else 0,
                                'analytics_id': value.get('analytics_id', False),
                            }
                            move_lines.append([0, 0, l_line])

                        move_lines.append([0, 0, {
                            'name': self.fiscal_year_id.name + _('year') + self.financial_carry_forward_id.name,
                            'account_id': line.carry_forward_in_account.id,
                            'debit': sum_debit if sum_debit > 0 else 0,
                            'credit': -sum_debit if sum_debit < 0 else 0,
                            'analytics_id': False,
                        }])
                    # 生成凭证时取当前日期所在年的最后一天
                    vals_move = {
                        'journal_id': self.env.ref('lumi_account.carry_forward_journal').id,
                        'period_id': target_period,
                        'date': last_year_day,
                        'company_id': self.company_id.id,
                        'abstract': self.fiscal_year_id.name + _('year') + self.financial_carry_forward_id.name,
                        'line_id': move_lines
                    }

                    if len(move_lines) > 1:
                        move_id = self.env['account.move'].create(vals_move)
                    else:
                        move_id = False

                    carry_forward_values = {
                        'carry_forward_name_id': line.carry_forward_name_id.id,
                        'carry_forward_period_id': target_period,
                        'carry_forward_account_lines': sql_value[0]['num'],
                        'carry_forward_debit_amount': sql_value[0]['debit'],
                        'carry_forward_credit_amount': sql_value[0]['credit'],
                        'carry_forward_account_move': move_id.id if move_id else False,
                        'run_end_closing_id': self.id
                    }
                    self.env['lumi.account.run.period.end.closing.line'].create(carry_forward_values)
                    self.env.cr.commit()
                except Exception as Error:
                    raise
            self.status = 'done'

    @api.multi
    def cancel_run_value(self):
        return {
            'type': 'ir.actions.act_window.message',
            'title': _('Notice'),
            'message': _('Are you sure to cancel carry forward result ?'),
            'buttons': [
                {
                    'type': 'method',
                    'name': _('Confirm'),
                    'model': 'lumi.account.run.period.end.closing',
                    'method': 'do_action_cancel',
                    'args': [self.id],
                    'kwargs': {'context': self.env.context},
                }
            ]
        }

    @api.model
    def do_action_cancel(self, id):
        self.env['lumi.account.run.period.end.closing.line']. \
            search([('run_end_closing_id', '=', id)]).mapped('carry_forward_account_move').unlink()
        self.browse(id).financial_carry_forward_ids.unlink()
        self.browse(id).write({'status': 'created'})
        return True

    # 跳转至凭证
    @api.model
    def open_account_move(self, params):
        for str_para in params:
            name, move_id = str_para.split(':')
            if name == 'carry_forward_account_move':
                move_id = int(move_id)
                view = self.env.ref('account.view_move_form')
                return {
                    'res_model': 'account.move',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view.id,
                    'name': _('Account Move'),
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': move_id if move_id else False,
                    'views': [(False, 'form')]
                }

    @api.multi
    def unlink(self):
        self.env['lumi.account.run.period.end.closing.line']. \
            search([('run_end_closing_id', 'in', self.ids)]).mapped('carry_forward_account_move').unlink()
        return super(LumiAccountRunPeriodEndClosing, self).unlink()

# 运行结转结果行
class LumiAccountRunPeriodEndClosingLine(models.Model):
    _name = 'lumi.account.run.period.end.closing.line'
    _description = 'Lumi Account Run Period End Closing Line'

    run_end_closing_id = fields.Many2one(comodel_name='lumi.account.run.period.end.closing', ondelete='cascade')

    # 年结/月结种类定义
    carry_forward_name_id = fields.Many2one(comodel_name='lumi.account.period.end.closing.structure',
                                            string='Carry Forward Name', help='Carry Forward Name')
    # 结转期间
    carry_forward_period_id = fields.Many2one(comodel_name='account.period', string='Carry Forward Period',
                                              help='Carry Forward Period')
    # 结账顺序
    carry_forward_order = fields.Integer(string='Carry Forward Order', help='Carry Forward Order',
                                         related='carry_forward_name_id.closing_order', readonly=True)
    # 结转凭证行
    carry_forward_account_lines = fields.Integer(string='Carry Forward Account Lines',
                                                 help='Carry Forward Account Lines')
    # 结转借方金额
    carry_forward_debit_amount = fields.Float(string='Carry Forward Debit Amount', help='Carry Forward Debit Amount')
    # 结转贷方金额
    carry_forward_credit_amount = fields.Float(string='Carry Forward Credit Amount', help='Carry Forward Credit Amount')
    # 结转凭证
    carry_forward_account_move = fields.Many2one(comodel_name='account.move', string='Carry Forward Account Move',
                                                 help='Carry Forward Account Move')
												 
												 
												 
	
	