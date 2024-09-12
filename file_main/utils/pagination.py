"""
自定义的分页组件,以后要使用这个组件可以直接导入
自定义的分页组件，以后如果想要使用这个分页组件，你需要做如下几件事

def pretty_iist(request):

    #1.根据自己的情况去筛选自己的数抓
    queryset=models.PrettyNum.objects.all()

    #2.实例化分页对象
    page_object =Pagination(request,queryset)
    context={
          "queryset":page_object.page_queryset,             #分完页的数据
          "page_string":page_object.html()                   #生成页码
          }
    return render(request,'pretty_iist.htm',context)

html中

{% for obj in querset %}
    {{obj.xx}}
{% endfor %}

<ul class="pagination">
    {{ page_string }}
</ul>

"""

from django.utils.safestring import mark_safe


class Pagination(object):
    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        # 优化url参数,使其可更改,保持原有参数
        # 如:xxx/?p=11   可更改为xxx/?p=11&q=12
        import copy
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        # query_dict.setlist("page", [11])
        self.query_dict = query_dict

        self.page_param = page_param
        # 检查get的page参数是否符合要求
        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1

        # 创建paginate所需参数
        self.page = page
        self.page_size = page_size
        self.start = (page - 1) * page_size
        self.end = page * page_size
        self.plus = plus

        self.page_queryset = queryset[self.start : self.end]

        total_count = queryset.count()
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        self.total_page_count = total_page_count

    def html(self):
        if self.total_page_count <= 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page_count
        else:
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        page_str_list = []

        self.query_dict.setlist(self.page_param,[1])
        page_str_list.append(f'<li><a href="?{self.query_dict.urlencode()}">首页</a></li>')

        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_param,[self.page-1])
            prev = f'<li><a href="?{self.query_dict.urlencode()}">上一页</a></li>'
        else:
            prev = f'<li class="disabled"><a href="#">上一页</a></li>'
        page_str_list.append(prev)

        # 页面
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param,[i])
            if i == self.page:
                ele = f'<li class="active"><a href="?{self.query_dict.urlencode()}">{i}</a></li>'
            else:
                ele = f'<li><a href="?{self.query_dict.urlencode()}">{i}</a></li>'
            page_str_list.append(ele)

        # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_param,[self.page + 1])
            next_page = (
                f'<li><a href="?{self.query_dict.urlencode()}">下一页</a></li>'
            )
        else:
            next_page = f'<li class="disabled"><a href="#">下一页</a></li>'
        page_str_list.append(next_page)

        # 尾页
        self.query_dict.setlist(self.page_param,[self.total_page_count])
        page_str_list.append(
            f'<li><a href="?{self.query_dict.urlencode()}">尾页</a></li>'
        )

        # 搜索框
        search_string = """
        <li>
            <form style="float:left;margin-left:-1px" method="get">
                <input name="page" style="position:relative;float:left;display:inline-block;width:88px;
                border-radius:4px;" type="text" class="form-control" placeholder="页码">
                <button style="border-radius: 4px" class="btn btn-default" type="submit">跳转</button>
            </form>
        </li>
        """
        page_str_list.append(search_string)

        page_string = mark_safe("".join(page_str_list))
        # print(page_string)
        return page_string
