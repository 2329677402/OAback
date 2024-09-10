from django.core.management.base import BaseCommand
from apps.oaauth.models import OADeparment


class Command(BaseCommand):

    def handle(self, *args, **options):
        # 初始化部门数据
        boarder = OADeparment.objects.create(name='董事会', intro='董事会')
        developer = OADeparment.objects.create(name='产品研发部', intro='产品设计, 技术开发')
        operator = OADeparment.objects.create(name='运营部', intro='产品运营, 用户运营')
        saler = OADeparment.objects.create(name='销售部', intro='销售产品')
        hr = OADeparment.objects.create(name='人事部', intro='员工招聘, 员工培训, 员工考核')
        finance = OADeparment.objects.create(name='财务部', intro='财务审核, 财务报表')
        self.stdout.write(self.style.SUCCESS('初始化部门数据成功!'))
