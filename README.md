https://docs.djangoproject.com/zh-hans/5.1/contents/

MTV 模型
Django 的 MTV 模式本质上和 MVC 是一样的，也是为了各组件间保持松耦合关系，只是定义上有些许不同，Django 的 MTV 分别是指：

M 表示模型（Model）：编写程序应有的功能，负责业务对象与数据库的映射(ORM)。
T 表示模板 (Template)：负责如何把页面(html)展示给用户。
V 表示视图（View）：负责业务逻辑，并在适当时候调用 Model和 Template。
除了以上三层之外，还需要一个 URL 分发器，它的作用是将一个个 URL 的页面请求分发给不同的 View 处理，View 再调用相应的 Model 和 Template，MTV 的响应模式如下所示：

## 创建项目
$ mkdir djangotutorial

然后，运行以下命令来引导一个新的 Django 项目：

$ django-admin startproject mysite djangotutorial

```
djangotutorial/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
```
这些目录和文件的用处是：

manage.py: 一个让你用各种方式管理 Django 项目的命令行工具。你可以阅读 [django-admin 和 manage.py](https://docs.djangoproject.com/zh-hans/5.1/ref/django-admin/) 获取所有 manage.py 的细节。

`mysite/`: 一个目录，它是你项目的实际 Python 包。它的名称是你需要用来导入其中任何内容的 Python 包名称（例如 mysite.urls）。

`mysite/__init__.py`：一个空文件，告诉 Python 这个目录应该被认为是一个 Python 包。如果你是 Python 初学者，阅读官方文档中的 [更多关于包的知识。]()

`mysite/settings.py`：Django 项目的配置文件。如果你想知道这个文件是如何工作的，请查看 Django 配置 了解细节。

`mysite/urls.py`：Django 项目的 URL 声明，就像你网站的“目录”。阅读 URL调度器 文档来获取更多关于 URL 的内容。

`mysite/asgi.py`：作为你的项目的运行在 ASGI 兼容的 Web 服务器上的入口。阅读 如何使用 ASGI 来部署 了解更多细节。

`mysite/wsgi.py`：作为你的项目的运行在 WSGI 兼容的Web服务器上的入口。阅读 如何使用 WSGI 进行部署 了解更多细节。

## 用于开发的简易服务器
让我们验证你的 Django 项目是否正常工作。如果还没有进入 djangotutorial 目录，请先进入该目录，然后运行以下命令：

在本地机器上启动一个轻量级的开发网络服务器:
```
$ python manage.py runserver
```
访问 http://127.0.0.1:8000/ 

## 创建投票应用

生成应用的基础目录结构

>应用是一个专门做某件事的网络应用程序——比如博客系统，或者公共记录的数据库，或者小型的投票程序。  
>项目则是一个网站使用的配置和应用的集合

创建一个应用：

```
$ python manage.py startapp polls
```
创建一个名为 polls 的应用

## 编写第一个视图¶
让我们开始编写第一个视图吧。打开 polls/views.py
```py
polls/views.py¶
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
```
映射到一个 URL

要为 polls 应用定义一个 URLconf，创建一个名为 polls/urls.py 的文件，并包含以下内容：

polls/urls.py¶
```py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

下一步是在 mysite 项目中配置全局 URLconf，以包含在 polls.urls 中定义的 URLconf。

为此，在 mysite/urls.py 中添加对 django.urls.include 的导入，并在 urlpatterns 列表中插入一个 include()，如下所示：

mysite/urls.py¶
```py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
]
```

设计 include() 的理念是使其可以即插即用

你现在把 index 视图添加进了 URLconf。通过以下命令验证是否正常工作：

```
$ python manage.py runserver
```

## 数据库配置¶
现在，打开 mysite/settings.py 。这是个包含了 Django 项目设置的 Python 模块。

- DATABASES 配置使用 SQLite。如果你是数据库新手，或者只是想尝试 Django，这是最简单的选择。SQLite 包含在 Python 中，因此你不需要安装任何其他东西来支持数据库。然而，当你开始第一个真正的项目时，你可能希望使用像 PostgreSQL 这样更具扩展性的数据库，以避免日后切换数据库的麻烦。


- TIME_ZONE 设置  为你自己时区。https://docs.djangoproject.com/zh-hans/5.1/ref/settings/#std-setting-TIME_ZONE

- INSTALLED_APPS 这里包括了会在你项目中启用的所有 Django 应用。应用能在多个项目中使用，你也可以打包并且发布应用，让别人使用它们。

```
python manage.py migrate
```

这个 migrate 命令查看 INSTALLED_APPS 配置，并根据 mysite/settings.py 文件中的数据库配置和随应用提供的数据库迁移文件（我们将在后面介绍这些），创建任何必要的数据库表。

## 创建模型
 polls/models.py
```py
from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

模型被表示为 django.db.models.Model 类的子类

字段都是 Field 类的实例

使用可选的选项来为 Field 定义一个人类可读的名字

使用 ForeignKey 定义了一个关系: 多对一、多对多和一对一。

## 激活模型

Django 可以：

- 为这个应用创建数据库 schema（生成 CREATE TABLE 语句）。

- 创建可以与 Question 和 Choice 对象进行交互的 Python 数据库 API。

但是首先得把 polls 应用安装到我们的项目里。

在配置类 INSTALLED_APPS 中添加设置。它的点式路径是 'polls.apps.PollsConfig'。在文件 mysite/settings.py 中 INSTALLED_APPS 子项添加点式路径后，它看起来像这样：
```
mysite/settings.py¶
INSTALLED_APPS = [
    "polls.apps.PollsConfig",

```

通过运行 makemigrations 命令，Django 会检测你对model文件的修改（在这种情况下，你已经取得了新的），并且把修改的部分储存为一次 迁移。

```
python manage.py makemigrations polls
```

你将会看到类似于下面这样的输出：
```
Migrations for 'polls':
  polls/migrations/0001_initial.py
    + Create model Question
    + Create model Choice
```
迁移是 Django 对于模型定义（也就是你的数据库结构）的变化的储存形式 - 它们其实也只是一些你磁盘上的文件。如果你想的话，你可以阅读一下你模型的迁移数据，它被储存在 polls/migrations/0001_initial.py 里。别担心，你不需要每次都阅读迁移文件，但是它们被设计成人类可读的形式，这是为了便于你手动调整 Django 的修改方式。

接收一个迁移的名称，然后返回对应的 SQL：
```
python manage.py sqlmigrate polls 0001
```


选中所有还没有执行过的迁移应用在数据库上，
创建任何必要的数据库表
```
python manage.py migrate
```
让你在开发过程中持续的改变数据库结构而不需要重新删除和创建表

改变模型需要这三步：

1. 编辑 models.py 文件，改变模型。

2. 运行 python manage.py makemigrations 为模型的改变生成迁移文件。

3. 运行 python manage.py migrate 来应用数据库迁移。

## 初试 API

进入交互式 Python 命令行，尝试一下 Django 为你创建的各种 API。通过以下命令打开 Python 命令行：

```
$ python manage.py shell
```

我们使用这个命令而不是简单的使用“python”是因为 manage.py 会设置 DJANGO_SETTINGS_MODULE 环境变量，这个变量会让 Django 根据 mysite/settings.py 文件来设置 Python 包的导入路径。

```py
>>> from polls.models import Choice, Question  # Import the model classes we just wrote.

# No questions are in the system yet.
>>> Question.objects.all()
<QuerySet []>

# Create a new Question.
# Support for time zones is enabled in the default settings file, so
# Django expects a datetime with tzinfo for pub_date. Use timezone.now()
# instead of datetime.datetime.now() and it will do the right thing.
>>> from django.utils import timezone
>>> q = Question(question_text="What's new?", pub_date=timezone.now())

# Save the object into the database. You have to call save() explicitly.
>>> q.save()

# Now it has an ID.
>>> q.id
1

# Access model field values via Python attributes.
>>> q.question_text
"What's new?"
>>> q.pub_date
datetime.datetime(2012, 2, 26, 13, 0, 0, 775217, tzinfo=datetime.timezone.utc)

# Change values by changing the attributes, then calling save().
>>> q.question_text = "What's up?"
>>> q.save()

# objects.all() displays all the questions in the database.
>>> Question.objects.all()
<QuerySet [<Question: Question object (1)>]>
```

<Question: Question object (1)> 对于我们了解这个对象的细节没什么帮助。让我们通过编辑 Question 模型的代码（位于 polls/models.py 中）来修复这个问题。给 Question 和 Choice 增加 __str__() 方法。
```py
polls/models.py¶
from django.db import models


class Question(models.Model):
    # ...
    def __str__(self):
        return self.question_text


class Choice(models.Model):
    # ...
    def __str__(self):
        return self.choice_text
```

给模型增加 __str__() 方法是很重要的，这不仅仅能给你在命令行里使用带来方便，Django 自动生成的 admin 里也使用这个方法来表示对象。

添加一个自定义方法：

polls/models.py¶
```py
import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    # ...
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
```

新加入的 import datetime 和 from django.utils import timezone 分别导入了 Python 的标准 datetime 模块和 Django 中和时区相关的 django.utils.timezone 工具模块。
```py
#无时区
import datetime
now = datetime.datetime.now()
#当启用了时区支持 (USE_TZ=True) ，Django 使用有时区日期时间对象。
from django.utils import timezone
now = timezone.now()
```

保存这些更改并再次运行 python manage.py shell 以启动新的 Python 交互式 shell：

```py
>>> from polls.models import Choice, Question

# Make sure our __str__() addition worked.
>>> Question.objects.all()
<QuerySet [<Question: What's up?>]>

# Django provides a rich database lookup API that's entirely driven by
# keyword arguments.
>>> Question.objects.filter(id=1)
<QuerySet [<Question: What's up?>]>
>>> Question.objects.filter(question_text__startswith="What")
<QuerySet [<Question: What's up?>]>

# Get the question that was published this year.
>>> from django.utils import timezone
>>> current_year = timezone.now().year
>>> Question.objects.get(pub_date__year=current_year)
<Question: What's up?>

# Request an ID that doesn't exist, this will raise an exception.
>>> Question.objects.get(id=2)
Traceback (most recent call last):
    ...
DoesNotExist: Question matching query does not exist.

# Lookup by a primary key is the most common case, so Django provides a
# shortcut for primary-key exact lookups.
# The following is identical to Question.objects.get(id=1).
>>> Question.objects.get(pk=1)
<Question: What's up?>

# Make sure our custom method worked.
>>> q = Question.objects.get(pk=1)
>>> q.was_published_recently()
True

# Give the Question a couple of Choices. The create call constructs a new
# Choice object, does the INSERT statement, adds the choice to the set
# of available choices and returns the new Choice object. Django creates
# a set (defined as "choice_set") to hold the "other side" of a ForeignKey
# relation (e.g. a question's choice) which can be accessed via the API.
>>> q = Question.objects.get(pk=1)

# Display any choices from the related object set -- none so far.
>>> q.choice_set.all()
<QuerySet []>

# Create three choices.
>>> q.choice_set.create(choice_text="Not much", votes=0)
<Choice: Not much>
>>> q.choice_set.create(choice_text="The sky", votes=0)
<Choice: The sky>
>>> c = q.choice_set.create(choice_text="Just hacking again", votes=0)

# Choice objects have API access to their related Question objects.
>>> c.question
<Question: What's up?>

# And vice versa: Question objects get access to Choice objects.
>>> q.choice_set.all()
<QuerySet [<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]>
>>> q.choice_set.count()
3

# The API automatically follows relationships as far as you need.
# Use double underscores to separate relationships.
# This works as many levels deep as you want; there's no limit.
# Find all Choices for any question whose pub_date is in this year
# (reusing the 'current_year' variable we created above).
>>> Choice.objects.filter(question__pub_date__year=current_year)
<QuerySet [<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]>

# Let's delete one of the choices. Use delete() for that.
>>> c = q.choice_set.filter(choice_text__startswith="Just hacking")
>>> c.delete()
```
## 介绍 Django 管理页面

### 创建一个管理员账号
首先，我们得创建一个能登录管理页面的用户。请运行下面的命令：

```
python manage.py createsuperuser
```

键入你想要使用的用户名，然后按下回车键：

Username: admin

然后提示你输入想要使用的邮件地址：

Email address: admin@example.com

最后一步是输入密码。你会被要求输入两次密码，第二次的目的是为了确认第一次输入的确实是你想要的密码。

Password: **********
Password (again): *********
Superuser created successfully.

### 启动开发服务器

Django 的管理界面默认就是启用的。让我们启动开发服务器，看看它到底是什么样的。

如果开发服务器未启动，用以下命令启动它：

```
python manage.py runserver
```

转到你本地域名的 “/admin/” 目录

### 进入管理站点页面¶
现在，试着使用你在上一步中创建的超级用户来登录。然后你将会看到 Django 管理页面的索引页：

Django 管理主页

你将会看到几种可编辑的内容：组和用户。它们是由 django.contrib.auth 提供的，这是 Django 开发的认证框架。

### 向管理页面中加入投票应用¶

但是我们的投票应用在哪呢？它没在索引页面里显示。

告诉管理，问题 Question 对象需要一个后台接口。打开 `polls/admin.py` 文件，把它编辑成下面这样：

polls/admin.py¶
```py
from django.contrib import admin

from .models import Question

admin.site.register(Question)
```
### 体验便捷的管理功能¶
现在我们向管理页面注册了问题 Question 类。Django 知道它应该被显示在索引页里：


点击 "Questions" 。现在看到是问题 "Questions" 对象的列表 "change list" 。这个界面会显示所有数据库里的问题 Question 对象，你可以选择一个来修改。

点击 “What's up?” 来编辑这个问题（Question）对象：

注意事项：

- 这个表单是从问题 Question 模型中自动生成的

- 不同的字段类型（日期时间字段 DateTimeField 、字符字段 CharField）会生成对应的 HTML 输入控件。每个类型的字段都知道它们该如何在管理页面里显示自己。

- 每个日期时间字段 DateTimeField 都有 JavaScript 写的快捷按钮。日期有转到今天（Today）的快捷按钮和一个弹出式日历界面。时间有设为现在（Now）的快捷按钮和一个列出常用时间的方便的弹出式列表。

页面的底部提供了几个选项：

- 保存（Save） - 保存改变，然后返回对象列表。

- 保存并继续编辑（Save and continue editing） - 保存改变，然后重新载入当前对象的修改界面。

- 保存并新增（Save and add another） - 保存改变，然后添加一个新的空对象并载入修改界面。

- 删除（Delete） - 显示一个确认删除页面。

如果显示的 “发布日期(Date Published)” 和你在 教程 1 里创建它们的时间不一致，这意味着你可能没有正确的设置 TIME_ZONE 。

点击“What's up?”对象页面右上角的 “历史(History)”按钮。你会看到一个列出了所有通过 Django 管理页面对当前对象进行的改变的页面，其中列出了时间戳和进行修改操作的用户名

## 创建公共接口——“视图”。
Django 中的视图的概念是「一类具有相同功能和模板的网页的集合」。

在 Django 中，网页和其他内容都是从视图派生而来。每一个视图表现为一个 Python 函数

URL 样式是 URL 的一般形式 - 例如：`/newsarchive/<year>/<month>/`。

为了将 URL 和视图关联起来，Django 使用了 'URLconfs' 来配置。URLconf 将 URL 模式映射到视图。

本教程只会介绍 URLconf 的基础内容，你可以看看 URL调度器 以获取更多内容。

## 编写更多视图

现在让我们向 `polls/views.py` 里添加更多视图。这些视图有一些不同，因为他们**接收参数**：

polls/views.py
```py
def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
```

把这些新视图添加进 polls.urls 模块里，只要添加几个 url() 函数调用就行：

polls/urls.py
```py
from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/5/
    path("<int:question_id>/", views.detail, name="detail"),
    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```

在浏览器中查看 "/polls/34/"。它将运行 detail() 函数并显示您在 URL 中提供的任何 ID。也可以尝试 "/polls/34/results/" 和 "/polls/34/vote/"，这些将显示占位的结果和投票页面。

当有人请求你网站的页面，比如说，"/polls/34/"，Django 会加载 mysite.urls Python 模块，因为它被 ROOT_URLCONF 设置指向。它会找到名为 urlpatterns 的变量并按顺序遍历这些模式。在找到匹配项 'polls/' 之后，它会剥离匹配的文本（"polls/"），然后将剩余的文本 -- "34/" -- 发送给 'polls.urls' URL 配置以进行进一步处理。在那里，它会与 '\<int:question_id\>/'匹配，从URL匹配到整数值，并将其分配给question_id参数，从而调用 detail() 视图，如下所示：

`detail(request=<HttpRequest object>, question_id=34)`
问题 question_id=34 来自 `<int:question_id>`。使用尖括号 "获得" 网址部分后发送给视图函数作为一个关键字参数。字符串的 question_id 部分定义了要使用的名字，用来识别相匹配的模式，而 int 部分是一种转换形式，用来确定应该匹配网址路径的什么模式。冒号 (\:\) 用来分隔转换形式和模式名。:)

## 写一个真正有用的视图

每个视图必须要做的只有两件事：
1. 返回一个包含被请求页面内容的 HttpResponse 对象，
或者
2. 抛出一个异常，比如 Http404 。

Django 只要求返回的是一个 HttpResponse ，或者抛出一个异常。

你的视图可以从数据库里读取记录，可以使用一个模板引擎（比如 Django 自带的，或者其他第三方的），可以生成一个 PDF 文件，可以输出一个 XML，创建一个 ZIP 文件，你可以做任何你想做的事，使用任何你想用的 Python 库。


因为 Django 自带的数据库 API 很方便，我们曾在 教程第 2 部分 中学过，所以我们试试在视图里使用它。我们在 index() 函数里插入了一些新内容，让它能展示数据库里以发布日期排序的最近 5 个投票问题，以空格分割：

polls/views.py
```py
from django.http import HttpResponse

from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    output = ", ".join([q.question_text for q in latest_question_list])
    return HttpResponse(output)


# Leave the rest of the views (detail, results, vote) unchanged
```

这里有个问题：页面的设计写死在视图函数的代码里的。如果你想改变页面的样子，你需要编辑 Python 代码。所以让我们使用 Django 的模板系统，只要创建一个视图，就可以将页面的设计从代码中分离出来。

首先，在你的 polls 目录里创建一个 templates 目录。Django 将会在这个目录里查找模板文件。

你项目的 TEMPLATES 配置项描述了 Django 如何载入和渲染模板。默认的设置文件设置了 DjangoTemplates 后端，并将 APP_DIRS 设置成了 True。这一选项将会让 DjangoTemplates 在每个 INSTALLED_APPS 文件夹中寻找 "templates" 子目录。这就是为什么尽管我们没有像在第二部分中那样修改 DIRS 设置，Django 也能正确找到 polls 的模板位置的原因。

在你刚刚创建的 templates 目录里，再创建一个目录 polls，然后在其中新建一个文件 index.html 。换句话说，你的模板文件的路径应该是 polls/templates/polls/index.html 。因为``app_directories`` 模板加载器是通过上述描述的方法运行的，所以 Django 可以引用到 polls/index.html 这一模板了。

>模板命名空间
>
>虽然我们现在可以将模板文件直接放在 polls/templates 文件夹中（而不是再建立一个 polls 子文件夹），但是这样做不太好。Django 将会选择第一个匹配的模板文件，如果你有一个模板文件正好和另一个应用中的某个模板文件重名，Django 没有办法 区分 它们。我们需要帮助 Django 选择正确的模板，最好的方法就是把他们放入各自的 命名空间 中，也就是把这些模板放入一个和 自身 应用重名的子文件夹里。

将下面的代码输入到刚刚创建的模板文件中：

polls/templates/polls/index.html
```
{% if latest_question_list %}
    <ul>
    {% for question in latest_question_list %}
        <li><a href="/polls/{{ question.id }}/">{{ question.question_text }}</a></li>
    {% endfor %}
    </ul>
{% else %}
    <p>No polls are available.</p>
{% endif %}
```

然后，让我们更新一下 polls/views.py 里的 index 视图来使用模板

polls/views.py¶
```py
from django.http import HttpResponse
from django.template import loader

from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("polls/index.html")
    context = {
        "latest_question_list": latest_question_list,
    }
    return HttpResponse(template.render(context, request))
```
上述代码的作用是，载入 polls/index.html 模板文件，并且向它传递一个上下文(context)。这个上下文是一个字典，它将模板内的变量映射为 Python 对象。

用你的浏览器访问 "/polls/" ，你将会看见一个无序列表，列出了我们在 教程第 2 部分 中添加的 “What's up” 投票问题，链接指向这个投票的详情页。

### 一个快捷函数： render()¶
「载入模板，填充上下文，再返回由它生成的 HttpResponse 对象」是一个非常常用的操作流程。于是 Django 提供了一个快捷函数，我们用它来重写 index() 视图：

polls/views.py¶
```py
from django.shortcuts import render

from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)
```
注意到，我们不再需要导入 loader 和 HttpResponse 。不过如果你还有其他函数（比如说 detail, results, 和 vote ）需要用到它的话，就需要保持 HttpResponse 的导入。

## 抛出 404 错误¶
现在，我们来处理投票详情视图——它会显示指定投票的问题标题。下面是这个视图的代码：

polls/views.py¶
```py
from django.http import Http404
from django.shortcuts import render

from .models import Question


# ...
def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/detail.html", {"question": question})
```

这里有个新原则。如果指定问题 ID 所对应的问题不存在，这个视图就会抛出一个 Http404 异常。

我们稍后再讨论你需要在 polls/detail.html 里输入什么，但是如果你想试试上面这段代码是否正常工作的话，你可以暂时把下面这段输进去：

polls/templates/polls/detail.html¶
```
{{ question }}
```
这样你就能测试了。

### 一个快捷函数： get_object_or_404()¶
尝试用 get() 函数获取一个对象，如果不存在就抛出 Http404 错误也是一个普遍的流程。Django 也提供了一个快捷函数，下面是修改后的详情 detail() 视图代码：

polls/views.py¶
```py
from django.shortcuts import get_object_or_404, render

from .models import Question


# ...
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})
```

>设计哲学
>
>为什么我们使用辅助函数 get_object_or_404() 而不是自己捕获 ObjectDoesNotExist 异常呢？还有，为什么模型 API 不直接抛出 ObjectDoesNotExist 而是抛出 Http404 呢？
>
>因为这样做会增加模型层和视图层的耦合性。指导 Django 设计的最重要的思想之一就是要保证松散耦合。一些受控的耦合将会被包含在 django.shortcuts 模块中。

也有 get_list_or_404() 函数，工作原理和 get_object_or_404() 一样，除了 get() 函数被换成了 filter() 函数。如果列表为空的话会抛出 Http404 异常。

## 使用模板系统¶
回过头去看看我们的 detail() 视图。它向模板传递了上下文变量 question 。下面是 polls/detail.html 模板里正式的代码：
```html
polls/templates/polls/detail.html¶
<h1>{{ question.question_text }}</h1>
<ul>
{% for choice in question.choice_set.all %}
    <li>{{ choice.choice_text }}</li>
{% endfor %}
</ul>
```
模板系统统一使用点符号来访问变量的属性。在示例 {{ question.question_text }} 中，首先 Django 尝试对 question 对象使用字典查找（也就是使用 obj.get(str) 操作），如果失败了就尝试属性查找（也就是 obj.str 操作），结果是成功了。如果这一操作也失败的话，将会尝试列表查找（也就是 obj[int] 操作）。

在 {% for %} 循环中发生的函数调用：question.choice_set.all 被解释为 Python 代码 question.choice_set.all() ，将会返回一个可迭代的 Choice 对象，这一对象可以在 {% for %} 标签内部使用。

查看 模板指南https://docs.djangoproject.com/zh-hans/5.1/topics/templates/ 可以了解关于模板的更多信息。

## 去除模板中的硬编码 URL¶
还记得吗，我们在 polls/index.html 里编写投票链接时，链接是硬编码的：

`<li><a href="/polls/{{ question.id }}/">{{ question.question_text }}</a></li>`

这种硬编码、强耦合的方法的问题在于，在具有大量模板的项目中更改 URL 变得具有挑战性。然而，由于你在 polls.urls 模块中的 path() 函数中定义了 name 参数，你可以通过使用 {% url %} 模板标签来消除对 url 配置中定义的特定 URL 路径的依赖：

`<li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>`
这个标签的工作方式是在 polls.urls 模块的 URL 定义中寻具有指定名字的条目。你可以回忆一下，具有名字 'detail' 的 URL 是在如下语句中定义的：

```py
# the 'name' value as called by the {% url %} template tag
path("<int:question_id>/", views.detail, name="detail"),
```
如果你想改变投票详情视图的 URL，比如想改成 polls/specifics/12/ ，你不用在模板里修改任何东西（包括其它模板），只要在 polls/urls.py 里稍微修改一下就行：

```py
# added the word 'specifics'
path("specifics/<int:question_id>/", views.detail, name="detail"),
```

## 为 URL 名称添加命名空间¶
教程项目只有一个应用，polls 。在一个真实的 Django 项目中，可能会有五个，十个，二十个，甚至更多应用。Django 如何分辨重名的 URL 呢？举个例子，polls 应用有 detail 视图，可能另一个博客应用也有同名的视图。Django 如何知道 `{% url %}` 标签到底对应哪一个应用的 URL 呢？

答案是：在根 URLconf 中添加命名空间。在 polls/urls.py 文件中稍作修改，加上 app_name 设置命名空间：

polls/urls.py¶
```py
from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```
现在，编辑 polls/index.html 文件，从：
```html
polls/templates/polls/index.html¶
<li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>
```
修改为指向具有命名空间的详细视图：
```html
polls/templates/polls/index.html¶
<li><a href="{% url 'polls:detail' question.id %}">{{ question.question_text }}</a></li>
```

## 编写一个简单的表单¶
让我们更新一下在上一个教程中编写的投票详细页面的模板 ("polls/detail.html") ，让它包含一个 HTML <form> 元素：

polls/templates/polls/detail.html¶
```html
<!-- 表单提交到指定URL，使用POST方法 -->
<form action="{% url 'polls:vote' question.id %}" method="post">
    {% csrf_token %}  <!-- Django安全机制，防止CSRF攻击 -->
    
    <fieldset>  <!-- 表单分组容器 -->
        <legend>  <!-- 分组的标题 -->
            <h1>{{ question.question_text }}</h1>  <!-- 显示问题文本 -->
        </legend>
        
        <!-- 错误提示 -->
        {% if error_message %}
        <p><strong>{{ error_message }}</strong></p>  <!-- 用粗体显示错误信息 -->
        {% endif %}
        
        <!-- 遍历所有选项 -->
        {% for choice in question.choice_set.all %}
            <!-- 单选按钮 -->
            <input type="radio" 
                   name="choice" 
                   id="choice{{ forloop.counter }}"  
                   value="{{ choice.id }}">   <!-- 同一组单选按钮 --><!-- 唯一ID生成（choice1/choice2...） --><!-- 提交的值为选项ID -->
            
            <!-- 关联标签 -->
            <label for="choice{{ forloop.counter }}">
                {{ choice.choice_text }}  <!-- 显示选项文本 -->
            </label><br>
        {% endfor %}
    </fieldset>
    
    <input type="submit" value="Vote">  <!-- 提交按钮 -->
</form>
```
简要说明：

- 上面的模板在 Question 的每个 Choice 前添加一个单选按钮。 每个单选按钮的 value 属性是对应的各个 Choice 的 ID。每个单选按钮的 name 是 "choice" 。这意味着，当有人选择一个单选按钮并提交表单提交时，它将发送一个 POST 数据 choice=# ，其中# 为选择的 Choice 的 ID。这是 HTML 表单的基本概念。

- 我们将表单的 action 设置为 {% url 'polls:vote' question.id %}，并设置 method="post"。使用 method="post" （而不是 method="get" ）是非常重要的，因为提交这个表单的行为将改变服务器端的数据。当你创建一个改变服务器端数据的表单时，使用 method="post"。这不是 Django 的特定技巧；这是优秀的网站开发技巧。

- forloop.counter 指示 for 标签已经循环多少次。

- 由于我们创建一个 POST 表单（它具有修改数据的作用），所以我们需要小心跨站点请求伪造。 谢天谢地，你不必太过担心，因为 Django 自带了一个非常有用的防御系统。 简而言之，所有针对内部 URL 的 POST 表单都应该使用 {% csrf_token %} 模板标签。

现在，让我们来创建一个 Django 视图来处理提交的数据。记住，在 教程第 3 部分 中，我们为投票应用创建了一个 URLconf ，包含这一行：

polls/urls.py¶
```py
path("<int:question_id>/vote/", views.vote, name="vote"),
```

我们还创建了一个 vote() 函数的虚拟实现。让我们来创建一个真实的版本。 将下面的代码添加到 polls/views.py ：

我们还创建了一个 vote() 函数的虚拟实现。让我们来创建一个真实的版本。 将下面的代码添加到 polls/views.py ：

polls/views.py¶
```py
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Choice, Question


# ...
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
```
以上代码中有些内容还未在本教程中提到过：

request.POST 是一个类字典对象，让你可以通过关键字的名字获取提交的数据。 这个例子中， request.POST['choice'] 以字符串形式返回选择的 Choice 的 ID。 request.POST 的值永远是字符串。

注意，Django 还以同样的方式提供 request.GET 用于访问 GET 数据 —— 但我们在代码中显式地使用 request.POST ，以保证数据只能通过 POST 调用改动。

如果在 request.POST['choice'] 数据中没有提供 choice ， POST 将引发一个 KeyError 。上面的代码检查 KeyError ，如果没有给出 choice 将重新显示 Question 表单和一个错误信息。

F("votes") + 1 指示数据库 将投票数增加 1。

在增加 Choice 的得票数之后，代码返回一个 HttpResponseRedirect 而不是常用的 HttpResponse 、 HttpResponseRedirect 只接收一个参数：用户将要被重定向的 URL（请继续看下去，我们将会解释如何构造这个例子中的 URL）。

正如上面的 Python 注释指出的，在成功处理 POST 数据后，你应该总是返回一个 HttpResponseRedirect。这不是 Django 的特殊要求，这是那些优秀网站在开发实践中形成的共识。

在这个例子中，我们在 HttpResponseRedirect 的构造函数中使用 reverse() 函数。这个函数避免了我们在视图函数中硬编码 URL。它需要我们给出我们想要跳转的视图的名字和该视图所对应的 URL 模式中需要给该视图提供的参数。 在本例中，使用在 教程第 3 部分 中设定的 URLconf， reverse() 调用将返回一个这样的字符串：

"/polls/3/results/"
其中 3 是 question.id 的值。重定向的 URL 将调用 'results' 视图来显示最终的页面。

正如在 教程第 3 部分 中提到的，request 是一个 HttpRequest 对象。更多关于 HttpRequest 对象的内容，请参见 请求和响应的文档 。

当有人对 Question 进行投票后， vote() 视图将请求重定向到 Question 的结果界面。让我们来编写这个视图：

polls/views.py¶
```py
from django.shortcuts import get_object_or_404, render


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})
```
这和 教程第 3 部分 中的 detail() 视图几乎一模一样。唯一的不同是模板的名字。 我们将在稍后解决这个冗余问题。

现在，创建一个 polls/results.html 模板：

polls/templates/polls/results.html¶
```html
{# 投票问题详情页模板 #}
{# 显示问题标题和所有选项的投票结果 #}

{# 显示当前投票问题的标题 #}
<h1>{{ question.question_text }}</h1>

{# 投票结果列表区域 #}
<ul>
{# 遍历该问题的所有选项对象 #}
{% for choice in question.choice_set.all %}
    {# 显示单个选项的文本和得票数 #}
    {# pluralize过滤器：当votes>1时自动添加"s"后缀 #}
    <li>{{ choice.choice_text }} -- {{ choice.votes }} vote{{ choice.votes|pluralize }}</li>
{% endfor %}
</ul>

{# 再次投票的链接 #}
{# 使用url模板标签生成指向投票详情页的URL #}
{# 'polls:detail' 是命名空间URL，question.id 是参数 #}
<a href="{% url 'polls:detail' question.id %}">Vote again?</a>
```
现在，在你的浏览器中访问 /polls/1/ 然后为 Question 投票。你应该看到一个投票结果页面，并且在你每次投票之后都会更新。 如果你提交时没有选择任何 Choice，你应该看到错误信息。

## 使用通用视图：代码还是少点好¶
detail() （在 教程第 3 部分 中）和 results() 视图都很精简 —— 并且，像上面提到的那样，存在冗余问题。显示投票列表的 index() 视图也具有类似性。

这些视图反映基本的网络开发中的一个常见情况：根据 URL 中的参数从数据库中获取数据、载入模板文件然后返回渲染后的模板。 由于这种情况特别常见，Django 提供一种快捷方式，叫做 “通用视图” 系统。

通用视图将常见的模式抽象到了一个地步，以至于你甚至不需要编写 Python 代码来创建一个应用程序。例如，ListView 和 DetailView 通用视图分别抽象了 "显示对象列表" 和 "显示特定类型对象的详细页面" 的概念。

让我们将我们的投票应用转换成使用通用视图系统，这样我们可以删除许多我们的代码。我们仅仅需要做以下几步来完成转换，我们将：

1. 转换 URLconf。

2. 删除一些旧的、不再需要的视图。

3. 基于 Django 的通用视图引入新的视图。

>为什么要重构代码？
>
>一般来说，当编写一个 Django 应用时，你应该先评估一下通用视图是否可以解决你的问题，你应该在一开始使用它，而不是进行到一半时重构代码。本教程目前为止是有意将重点放在以“艰难的方式”编写视图，这是为将重点放在核心概念上。

### 改良 URLconf¶
首先，打开 polls/urls.py 这个 URLconf 并将它修改成：

polls/urls.py¶
```PY
from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]
```
请注意，第二和第三个模式的路径字符串中匹配的模式名称已从 <question_id> 更改为 <pk>。这是因为我们将使用 DetailView 通用视图来替换我们的 detail() 和 results() 视图，它期望从 URL 中捕获的主键值被称为 "pk"。

### 改良视图¶
下一步，我们将删除旧的 index, detail, 和 results 视图，并用 Django 的通用视图代替。打开 polls/views.py 文件，并将它修改成：

polls/views.py¶
```py
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    # same as above, no changes needed.
    ...
```

每个通用视图都需要知道它将要操作的模型。可以使用 `model` 属性来提供这个信息（在这个示例中，对于 DetailView 和 ResultsView，是 model = Question），或者通过定义 `get_queryset()` 方法来实现（如 IndexView 中所示）。

默认情况下，通用视图 DetailView 使用一个叫做 `<app name>/<model name>_detail.html` 的模板。在我们的例子中，它将使用 "polls/question_detail.html" 模板。template_name 属性是用来告诉 Django 使用一个指定的模板名字，而不是自动生成的默认名字。 我们也为 results 列表视图指定了 template_name —— 这确保 results 视图和 detail 视图在渲染时具有不同的外观，即使它们在后台都是同一个 DetailView 。

类似地，ListView 使用一个叫做 `<app name>/<model name>_list.html` 的默认模板；我们使用 template_name 来告诉 ListView 使用我们创建的已经存在的 "polls/index.html" 模板。

在之前的教程中，提供模板文件时都带有一个包含 question 和 latest_question_list 变量的 context。对于 DetailView ， question 变量会自动提供—— 因为我们使用 Django 的模型（Question）， Django 能够为 context 变量决定一个合适的名字。然而对于 ListView， 自动生成的 context 变量是 question_list。为了覆盖这个行为，我们提供 context_object_name 属性，表示我们想使用 latest_question_list。作为一种替换方案，你可以改变你的模板来匹配新的 context 变量 —— 这是一种更便捷的方法，告诉 Django 使用你想使用的变量名。

启动服务器，使用一下基于通用视图的新投票应用。

更多关于通用视图的详细信息，请查看 通用视图的文档

当你对你所写的表单和通用视图感到满意后，请阅读 教程的第 5 部分 来了解如何测试我们的投票应用。

## 自动化测试简介¶
### 自动化测试是什么？¶
测试代码，是用来检查你的代码能否正常运行的程序。

测试在不同的层次中都存在。有些测试只关注某个很小的细节（某个模型的某个方法的返回值是否满足预期？），而另一些测试可能检查对某个软件的一系列操作（某一用户输入序列是否造成了预期的结果？）

自动化 测试是由某个系统帮你自动完成的。当你创建好了一系列测试，每次修改应用代码后，就可以自动检查出修改后的代码是否还像你曾经预期的那样正常工作。你不需要花费大量时间来进行手动测试。

### 为什么你需要写测试¶
#### 测试将节约你的时间¶
在某种程度上，能够「判断出代码是否正常工作」的测试，就称得上是个令人满意的了。在更复杂的应用程序中，组件之间可能会有数十个复杂的交互。

对其中某一组件的改变，也有可能会造成意想不到的结果。判断「代码是否正常工作」意味着你需要用大量的数据来完整的测试全部代码的功能，以确保你的小修改没有对应用整体造成破坏——这太费时间了。

尤其是当你发现自动化测试能在几秒钟之内帮你完成这件事时，就更会觉得手动测试实在是太浪费时间了。当某人写出错误的代码时，自动化测试还能帮助你定位错误代码的位置。

有时候你会觉得，和富有创造性和生产力的业务代码比起来，编写枯燥的测试代码实在是太无聊了，特别是当你知道你的代码完全没有问题的时候。

然而，编写测试还是要比花费几个小时手动测试你的应用，或者为了找到某个小错误而胡乱翻看代码要有意义的多。

#### 测试不仅能发现错误，而且能预防错误¶
「测试是开发的对立面」，这种思想是不对的。

如果没有测试，整个应用的行为意图会变得更加的不清晰。甚至当你在看自己写的代码时也是这样，有时候你需要仔细研读一段代码才能搞清楚它有什么用。

而测试的出现改变了这种情况。测试就好像是从内部仔细检查你的代码，当有些地方出错时，这些地方将会变得很显眼——就算你自己没有意识到那里写错了。

#### 测试使你的代码更有吸引力¶
你也许遇到过这种情况：你编写了一个绝赞的软件，但是其他开发者看都不看它一眼，因为它缺少测试。没有测试的代码不值得信任。 Django 最初开发者之一的 Jacob Kaplan-Moss 说过：“项目规划时没有包含测试是不科学的。”

其他的开发者希望在正式使用你的代码前看到它通过了测试，这是你需要写测试的另一个重要原因。

#### 测试有利于团队协作¶
前面的几点都是从单人开发的角度来说的。复杂的应用可能由团队维护。测试的存在保证了协作者不会不小心破坏了了你的代码（也保证你不会不小心弄坏他们的）。如果你想作为一个 Django 程序员谋生的话，你必须擅长编写测试！

开始写我们的第一个测试¶
首先得有个 Bug¶
幸运的是，我们的 polls 应用现在就有一个小 bug 需要被修复：我们的要求是如果 Question 是在一天之内发布的， Question.was_published_recently() 方法将会返回 True ，然而现在这个方法在 Question 的 pub_date 字段比当前时间还晚时也会返回 True（这是个 Bug）。

用 shell 命令确认一下这个方法的日期bug

/ 
$ python manage.py shell
>>> import datetime
>>> from django.utils import timezone
>>> from polls.models import Question
>>> # create a Question instance with pub_date 30 days in the future
>>> future_question = Question(pub_date=timezone.now() + datetime.timedelta(days=30))
>>> # was it published recently?
>>> future_question.was_published_recently()
True
因为将来发生的是肯定不是最近发生的，所以代码明显是错误的。

创建一个测试来暴露这个 bug¶
我们刚刚在 shell 里做的测试也就是自动化测试应该做的工作。所以我们来把它改写成自动化的吧。

按照惯例，Django 应用的测试应该写在应用的 tests.py 文件里。测试系统会自动的在所有文件里寻找并执行以 test 开头的测试函数。

将下面的代码写入 polls 应用里的 tests.py 文件内：

polls/tests.py¶
import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
我们创建了一个 django.test.TestCase 的子类，并添加了一个方法，此方法创建一个 pub_date 时未来某天的 Question 实例。然后检查它的 was_published_recently() 方法的返回值——它 应该 是 False。

运行测试¶
在终端中，我们通过输入以下代码运行测试:

/ 
$ python manage.py test polls
你将看到类似以下的内容：

Creating test database for alias 'default'...
System check identified no issues (0 silenced).
F
======================================================================
FAIL: test_was_published_recently_with_future_question (polls.tests.QuestionModelTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/path/to/djangotutorial/polls/tests.py", line 16, in test_was_published_recently_with_future_question
    self.assertIs(future_question.was_published_recently(), False)
AssertionError: True is not False

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
Destroying test database for alias 'default'...
不一样的错误？

若在此处你得到了一个 NameError 错误，你可能漏了 第二步 中将 datetime 和 timezone 导入 polls/model.py 的步骤。复制这些语句，然后试着重新运行测试。

发生了什么呢？以下是自动化测试的运行过程：

python manage.py test polls 将会寻找 polls 应用里的测试代码

它找到了 django.test.TestCase 的一个子类

它创建一个特殊的数据库供测试使用

它在类中寻找测试方法——以 test 开头的方法。

在 test_was_published_recently_with_future_question 方法中，它创建了一个 pub_date 值为 30 天后的 Question 实例。

接着使用 assertls() 方法，发现 was_published_recently() 返回了 True，而我们期望它返回 False。

测试系统通知我们哪些测试样例失败了，和造成测试失败的代码所在的行号。

修复这个 bug¶
我们早已知道，当 pub_date 为未来某天时， Question.was_published_recently() 应该返回 False。我们修改 models.py 里的方法，让它只在日期是过去式的时候才返回 True：

polls/models.py¶
def was_published_recently(self):
    now = timezone.now()
    return now - datetime.timedelta(days=1) <= self.pub_date <= now
然后再次运行测试：

Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
Destroying test database for alias 'default'...
发现 bug 后，我们编写了能够暴露这个 bug 的自动化测试。在修复 bug 之后，我们的代码顺利的通过了测试。

将来，我们的应用可能会出现其他的问题，但是我们可以肯定的是，一定不会再次出现这个 bug，因为只要运行一遍测试，就会立刻收到警告。我们可以认为应用的这一小部分代码永远是安全的。

更全面的测试¶
我们已经搞定一小部分了，现在可以考虑全面的测试 was_published_recently() 这个方法以确定它的安全性，然后就可以把这个方法稳定下来了。事实上，在修复一个 bug 时不小心引入另一个 bug 会是非常令人尴尬的。

我们在上次写的类里再增加两个测试，来更全面的测试这个方法：

polls/tests.py¶
def test_was_published_recently_with_old_question(self):
    """
    was_published_recently() returns False for questions whose pub_date
    is older than 1 day.
    """
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    self.assertIs(old_question.was_published_recently(), False)


def test_was_published_recently_with_recent_question(self):
    """
    was_published_recently() returns True for questions whose pub_date
    is within the last day.
    """
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    recent_question = Question(pub_date=time)
    self.assertIs(recent_question.was_published_recently(), True)
现在，我们有三个测试来确保 Question.was_published_recently() 方法对于过去，最近，和将来的三种情况都返回正确的值。

再次申明，尽管 polls 现在是个小型的应用，但是无论它以后变得到多么复杂，无论他和其他代码如何交互，我们可以在一定程度上保证我们为之编写测试的方法将按照预期的方式运行。

测试视图¶
我们的投票应用对所有问题都一视同仁：它将会发布所有的问题，也包括那些 pub_date 字段值是未来的问题。我们应该改善这一点。如果 pub_date 设置为未来某天，这应该被解释为这个问题将在所填写的时间点才被发布，而在之前是不可见的。

针对视图的测试¶
为了修复上述 bug ，我们这次先编写测试，然后再去改代码。事实上，这是一个「测试驱动」开发模式的实例，但其实这两者的顺序不太重要。

在我们的第一个测试中，我们关注代码的内部行为。我们通过模拟用户使用浏览器访问被测试的应用来检查代码行为是否符合预期。

在我们动手之前，先看看需要用到的工具们。

Django 测试工具之 Client¶
Django 提供了一个供测试使用的 Client 来模拟用户和视图层代码的交互。我们能在 tests.py 甚至是 shell 中使用它。

我们依照惯例从 shell 开始，首先我们要做一些在 tests.py 里不是必须的准备工作。第一步是在 shell 中配置测试环境:

/ 
$ python manage.py shell
>>> from django.test.utils import setup_test_environment
>>> setup_test_environment()
setup_test_environment() 安装了一个模板渲染器，这将使我们能够检查响应上的一些额外属性，如 response.context，否则将无法使用此功能。请注意，这个方法 不会 建立一个测试数据库，所以下面的内容将针对现有的数据库运行，输出结果可能略有不同，这取决于你已经创建了哪些问题。如果你在 settings.py 中的 TIME_ZONE 不正确，你可能会得到意外的结果。如果你不记得之前的配置，请在继续之前检查。

接下来，我们需要导入测试客户端类（稍后在 tests.py 中，我们将使用 django.test.TestCase 类，它自带一个客户端，所以这个步骤不是必需的）：

>>> from django.test import Client
>>> # create an instance of the client for our use
>>> client = Client()
准备好后，我们可以要求客户端为我们执行一些工作：

>>> # get a response from '/'
>>> response = client.get("/")
Not Found: /
>>> # we should expect a 404 from that address; if you instead see an
>>> # "Invalid HTTP_HOST header" error and a 400 response, you probably
>>> # omitted the setup_test_environment() call described earlier.
>>> response.status_code
404
>>> # on the other hand we should expect to find something at '/polls/'
>>> # we'll use 'reverse()' rather than a hardcoded URL
>>> from django.urls import reverse
>>> response = client.get(reverse("polls:index"))
>>> response.status_code
200
>>> response.content
b'\n    <ul>\n    \n        <li><a href="/polls/1/">What&#x27;s up?</a></li>\n    \n    </ul>\n\n'
>>> response.context["latest_question_list"]
<QuerySet [<Question: What's up?>]>
改善视图代码¶
现在的投票列表会显示将来的投票（ pub_date 值是未来的某天)。我们来修复这个问题。

在 教程的第 4 部分 里，我们介绍了基于 ListView 的视图类：

polls/views.py¶
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]
我们需要改进 get_queryset() 方法，让他它能通过将 Question 的 pub_data 属性与 timezone.now() 相比较来判断是否应该显示此 Question。首先我们需要一行 import 语句：

polls/views.py¶
from django.utils import timezone
然后我们把 get_queryset 方法改写成下面这样：

polls/views.py¶
def get_queryset(self):
    """
    Return the last five published questions (not including those set to be
    published in the future).
    """
    return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
        :5
    ]
Question.objects.filter(pub_date__lte=timezone.now()) returns a queryset containing Questions whose pub_date is less than or equal to - that is, earlier than or equal to - timezone.now().

测试新视图¶
启动服务器、在浏览器中载入站点、创建一些发布时间在过去和将来的 Questions ，然后检验只有已经发布的 Questions 会展示出来，现在你可以对自己感到满意了。你不想每次修改可能与这相关的代码时都重复这样做 —— 所以让我们基于以上 shell 会话中的内容，再编写一个测试。

将下面的代码添加到 polls/tests.py ：

polls/tests.py¶
from django.urls import reverse
然后我们写一个公用的快捷函数用于创建投票问题，再为视图创建一个测试类：

polls/tests.py¶
def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )
让我们更详细地看下以上这些内容。

首先是一个快捷函数 create_question，它封装了创建投票的流程，减少了重复代码。

test_no_questions 不会创建任何问题，但会检查消息 "No polls are available." 并验证 latest_question_list 是否为空。注意，django.test.TestCase 类提供了一些额外的断言方法。在这些示例中，我们使用了 assertContains() 和 assertQuerySetEqual()。

在 test_past_question 方法中，我们创建了一个投票并检查它是否出现在列表中。

在 test_future_question 中，我们创建 pub_date 在未来某天的投票。数据库会在每次调用测试方法前被重置，所以第一个投票已经没了，所以主页中应该没有任何投票。

剩下的那些也都差不多。实际上，测试就是假装一些管理员的输入，然后通过用户端的表现是否符合预期来判断新加入的改变是否破坏了原有的系统状态。

测试 DetailView¶
我们的工作似乎已经很完美了？不，还有一个问题：就算在发布日期时未来的那些投票不会在目录页 index 里出现，但是如果用户知道或者猜到正确的 URL ，还是可以访问到它们。所以我们得在 DetailView 里增加一些约束：

polls/views.py¶
class DetailView(generic.DetailView):
    ...

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
然后，我们应该增加一些测试来检验 pub_date 在过去的 Question 能够被显示出来，而 pub_date 在未来的则不可以：

polls/tests.py¶
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
更多的测试思路¶
我们应该给 ResultsView 也增加一个类似的 get_queryset 方法，并且为它创建测试。这和我们之前干的差不多，事实上，基本就是重复一遍。

我们还可以从各个方面改进投票应用，但是测试会一直伴随我们。比方说，在目录页上显示一个没有选项 Choices 的投票问题就没什么意义。我们可以检查并排除这样的投票题。测试可以创建一个没有选项的投票，然后检查它是否被显示在目录上。当然也要创建一个有选项的投票，然后确认它确实被显示了。

恩，也许你想让管理员能在目录上看见未被发布的那些投票，但是普通用户看不到。不管怎么说，如果你想要增加一个新功能，那么同时一定要为它编写测试。不过你是先写代码还是先写测试那就随你了。

在未来的某个时刻，你一定会去查看测试代码，然后开始怀疑：「这么多的测试不会使代码越来越复杂吗？」。别着急，我们马上就会谈到这一点。

当需要测试的时候，测试用例越多越好¶
貌似我们的测试多的快要失去控制了。按照这样发展下去，测试代码就要变得比应用的实际代码还要多了。而且测试代码大多都是重复且不优雅的，特别是在和业务代码比起来的时候，这种感觉更加明显。

但是这没关系！ 就让测试代码继续肆意增长吧。大部分情况下，你写完一个测试之后就可以忘掉它了。在你继续开发的过程中，它会一直默默无闻地为你做贡献的。

但有时测试也需要更新。想象一下如果我们修改了视图，只显示有选项的那些投票，那么只前写的很多测试就都会失败。但这也明确地告诉了我们哪些测试需要被更新，所以测试也会测试自己。

最坏的情况是，当你继续开发的时候，发现之前的一些测试现在看来是多余的。但是这也不是什么问题，多做些测试也 不错。

如果你对测试有个整体规划，那么它们就几乎不会变得混乱。下面有几条好的建议：

对于每个模型和视图都建立单独的 TestClass

每个测试方法只测试一个功能

给每个测试方法起个能描述其功能的名字

深入代码测试¶
在本教程中，我们仅仅是了解了测试的基础知识。你能做的还有很多，而且世界上有很多有用的工具来帮你完成这些有意义的事。

举个例子，在上述的测试中，我们已经从代码逻辑和视图响应的角度检查了应用的输出，现在你可以从一个更加 "in-browser" 的角度来检查最终渲染出的 HTML 是否符合预期，使用 Selenium 可以很轻松的完成这件事。这个工具不仅可以测试 Django 框架里的代码，还可以检查其他部分，比如说你的 JavaScript。它假装成是一个正在和你站点进行交互的浏览器，就好像有个真人在访问网站一样！Django 它提供了 LiveServerTestCase 来和 Selenium 这样的工具进行交互。

如果你在开发一个很复杂的应用的话，你也许想在每次提交代码时自动运行测试，也就是我们所说的持续集成 continuous integration ，这样就能实现质量控制的自动化，起码是部分自动化。

一个找出代码中未被测试部分的方法是检查代码覆盖率。它有助于找出代码中的薄弱部分和无用部分。如果你无法测试一段代码，通常说明这段代码需要被重构或者删除。想知道代码覆盖率和无用代码的详细信息，查看文档 集成 coverage.py 获取详细信息。

文档 Django 中的测试 里有关于测试的更多信息。

