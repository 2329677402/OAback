from django.core.management.base import BaseCommand
from apps.oaauth.models import OADeparment, OAUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        boarder = OADeparment.objects.get(name='董事会')
        developer = OADeparment.objects.get(name='产品研发部')
        operator = OADeparment.objects.get(name='运营部')
        saler = OADeparment.objects.get(name='销售部')
        hr = OADeparment.objects.get(name='人事部')
        finance = OADeparment.objects.get(name='财务部')

        # 初始化用户数据
        # 董事会的员工, 都是superuser用户
        # 1、东东: 属于董事会的leader
        dongdong = OAUser.objects.create_superuser(email="dongdong@qq.com", realname='东东', password='111111',
                                                   department=boarder)

        # 2、多多: 董事会
        duoduo = OAUser.objects.create_superuser(email="duoduo@qq.com", realname='多多', password='111111',
                                                 department=boarder)

        # 3、张三: 产品研发部的leader
        zhangsan = OAUser.objects.create_user(email="zhangsan@qq.com", realname='张三', password='111111',
                                              department=developer)

        # 4、李四: 运营部的leader
        lisi = OAUser.objects.create_user(email="lisi@qq.com", realname='李四', password='111111',
                                          department=operator)

        # 5、王五: 销售部的leader
        wangwu = OAUser.objects.create_user(email="wangwu@qq.com", realname='王五', password='111111',
                                            department=saler)

        # 6、赵六: 人事部的leader
        zhaoliu = OAUser.objects.create_user(email="zhaoliu@qq.com", realname='赵六', password='111111',
                                             department=hr)

        # 7、孙七: 财务部的leader
        sunqi = OAUser.objects.create_user(email="sunqi@qq.com", realname='孙七', password='111111',
                                           department=finance)

        # 给部门指定leader和manager
        # 分管部门
        # 东东: 产品研发部, 运营部、销售部
        # 多多: 人事部、财务部
        # 1、董事会
        boarder.leader = dongdong
        boarder.manager = None

        # 2、产品研发部
        developer.leader = zhangsan
        developer.manager = dongdong

        # 3、运营部
        operator.leader = lisi
        operator.manager = dongdong

        # 4、销售部
        saler.leader = wangwu
        saler.manager = dongdong

        # 5、人事部
        hr.leader = zhaoliu
        hr.manager = duoduo

        # 6、财务部
        finance.leader = sunqi
        finance.manager = duoduo

        # 保存用户数据
        boarder.save()
        developer.save()
        operator.save()
        saler.save()
        hr.save()
        finance.save()
        self.stdout.write(self.style.SUCCESS('初始化用户数据成功!'))
