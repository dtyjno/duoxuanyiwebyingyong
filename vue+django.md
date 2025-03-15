## Web应用模式
### 单页应用（SPA）或多页应用（MPA）
#### 多页面应用-传统Web应用模式（Multi-Page Application, MPA）
https://blog.csdn.net/zzx262625/article/details/134486999

定义：多页面应用指的是每个页面对应一个独立的HTML文件，用户在访问不同页面时会加载新的HTML页面

特点：用户每次操作（如点击链接或提交表单）都会导致页面刷新，服务器返回新的HTML页面。

优点：
- SEO友好，搜索引擎可以轻松抓取页面内容。 
- 技术实现简单，适合内容型网站（如博客、新闻网站）。

缺点：
- 页面刷新导致用户体验较差。
- 服务器负载较高，因为每次请求都需要生成完整的HTML页面。
- 前后端耦合度高，开发和维护成本可能较高。

典型技术：PHP、JSP、ASP.NET、Ruby on Rails等。

#### 单页应用模式（Single-Page Application, SPA）

特点：整个应用只有一个HTML页面（初始页面），动态加载和更新内容通过JavaScript（通过Ajax和动态DOM操作）实现，无需刷新页面。

优点：
 
SEO友好，页面内容在服务器端生成。
 
首屏加载速度快，用户直接看到渲染好的内容。
 
缺点：
 
服务器负载较高，每次请求都需要生成页面。
 
开发复杂度较高，需要处理服务器和客户端的渲染逻辑。
 
典型技术：Next.js（React）、Nuxt.js（Vue.js）、PHP模板引擎等。

### 三种渲染方式

客户端渲染 BSR (Broswer Side Render)   
静态页面生成 SSG (Static Site Generation)   
服务端渲染 SSR (Server Side Render)  

BSR -- 用 JS、Vue、React 创建 HTML
SSG -- 页面静态化，把 PHP 提前渲染成 HTML
SSR -- PHP、Python、Ruby、Java 后台的基本功能

#### 3. 服务器端渲染模式（Server-Side Rendering, SSR）
 
特点：服务器在收到请求时生成HTML页面并返回给客户端，页面内容在服务器端渲染完成。
 
优点：
 
SEO友好，页面内容在服务器端生成。
 
首屏加载速度快，用户直接看到渲染好的内容。
 
缺点：
 
服务器负载较高，每次请求都需要生成页面。
 
开发复杂度较高，需要处理服务器和客户端的渲染逻辑。
 
典型技术：Next.js（React）、Nuxt.js（Vue.js）、PHP模板引擎等。
 
 
#### 4. 静态站点生成模式（Static Site Generation, SSG）
 
特点：在构建时生成静态HTML文件，用户访问时直接返回这些静态文件，无需动态生成。
 
优点：
 
性能极高，静态文件可以直接通过CDN分发。
 
SEO友好，内容在构建时生成。
 
缺点：
 
不适合频繁更新的内容。
 
需要重新构建以更新内容。
 
典型技术：Gatsby、Hugo、Jekyll等。

### App开发
#### PWA (Progressive Web App)
PWA 是 Google 公司提出的一种新型应用程序开发技术，它融合了 Web 和 App 的优点，旨在提高 Web 应用程序的用户体验和性能。PWA 可以将 Web 应用程序变成一个可离线访问的应用，具有离线缓存、本地推送通知等能力，用户可以在手机桌面上添加 PWA 应用的图标，并像本地应用程序一样进行启动和使用。

PWA 所适用的场景主要是用户在离线或者网络不佳的情况下仍然需要使用 Web 应用程序。

PWA 运用了 Service Worker 技术进行页面的快速缓存，实现离线访问和本地推送等功能。

#### 渐进式 Web 应用（Progressive Web App，PWA）
https://developer.mozilla.org/zh-CN/docs/Web/Progressive_web_apps/Guides/Best_practices

https://learn.microsoft.com/zh-cn/microsoft-edge/progressive-web-apps-chromium/how-to/best-practices


 web 平台技术构建的应用程序，但它提供的用户体验就像一个特定平台的应用程序，支持跨平台使用，充分实现了“Write once, Run everywhere”的理念。

可以由浏览器提示以将其安装在设备上。安装后，PWA 对用户而言就是特定于平台的应用程序，用户可以像启动其他任何应用程序一样直接从操作系统启动它。

### 前后端交互
在开发Web应用中，有两种应用模式：

- 前后端不分离
- 前后端分离

#### 1. 前后端分离（Frontend-Backend Separation）
 
特点：
 
职责分离：
 
前端：负责用户界面（UI）、交互逻辑、数据渲染（如SPA）。
 
后端：仅提供API接口（如RESTful API或GraphQL），处理业务逻辑、数据库操作和安全性。
 
通信方式：前后端通过HTTP API（如JSON/XML）交互，前端通过Ajax/Fetch等方式请求数据。
 
 在前后端分离的应用模式中，我们通常将后端开发的每个视图都称为一个接口，或者API，前端通过访问接口来对数据进行增删改查。

技术栈独立：
 
前端使用框架（React、Vue、Angular）和工具链（Webpack、Vite）。
 
后端使用Java、Python、Node.js等，专注于服务层。
 
部署独立：前端和后端可以独立部署，前端通常托管在CDN或静态服务器，后端部署在应用服务器。
 
优点：
 
并行开发：前后端团队可独立工作，仅需约定API接口。
 
灵活性高：前端可快速迭代UI，后端可专注于性能优化和扩展。
 
跨平台支持：同一后端API可同时服务于Web、移动端（iOS/Android）或其他客户端。
 
性能优化：前端可通过缓存、懒加载等技术提升用户体验。
 
缺点：
 
SEO不友好：纯前端渲染（CSR）需要额外优化（如SSR或预渲染）。
 
首屏加载慢：首次需加载大量JavaScript文件。
 
复杂度高：需管理跨域、接口版本控制、状态同步等问题。
 
适用场景：
 
复杂单页应用（SPA）或管理后台。
 
多终端（Web、移动端）需要共享同一API。
 
团队规模较大，需分工协作。
 
 
#### 2. 前后端融合（Frontend-Backend Integration）
 
特点：
 
职责耦合：
 
后端直接生成HTML页面（如服务端渲染SSR），前端代码与后端逻辑混合（如模板引擎）。
 
通信方式：用户请求直接由后端处理，后端渲染完整页面后返回给浏览器。
 
技术栈绑定：
 
使用模板引擎（如Jinja2、Thymeleaf、EJS）或全栈框架（如Ruby on Rails、Laravel）。
 
部署一体：前后端代码通常部署在同一服务器，难以完全解耦。
 
优点：
 
SEO友好：页面内容在服务端直接生成，搜索引擎易抓取。
 
首屏加载快：用户直接看到渲染后的HTML，无需等待JavaScript执行。
 
开发简单：适合小型项目或内容型网站（如博客、新闻站）。
 
缺点：
 
开发效率低：前后端强耦合，修改需同步调整。
 
扩展性差：难以支持多终端（如移动端需单独开发API）。
 
技术栈限制：前端无法灵活使用现代框架的交互特性。
 
适用场景：
 
内容为主的网站（如企业官网、CMS系统）。
 
快速原型开发或小型项目。
 
对SEO要求高的场景。


 
4. 现代趋势：混合模式
在实际开发中，两种模式常结合使用：
 
服务端渲染（SSR）与客户端渲染（CSR）结合：
例如Next.js/Nuxt.js，首屏由服务端渲染（SEO友好），后续交互由前端接管（SPA体验）。
 
BFF（Backend for Frontend）模式：
后端为不同客户端（Web、移动端）定制API，兼顾分离的灵活性与业务逻辑的集中管理。
 
 
如何选择？
 
选择前后端分离：
项目复杂、多终端支持、团队协作要求高。
 
选择前后端融合：
简单内容型网站、快速开发、SEO优先级高。
 
混合模式：
平衡SEO与交互体验（如电商网站、社交媒体）。

## Django REST framework前后端分离框架
https://www.django-rest-framework.org/

https://blog.csdn.net/zhangyifeng_1995/article/details/131898576

它为开发人员提供了一套快速开发 RESTful API 的工具，它能够自动化 API 可视化、文档化，实现接口的自动化测试以及自动化的API路由、序列化、视图、验证、分页、版本管理、认证等等功能

### Django REST 安装

REST 框架需要以下内容：

Django （4.2、5.0、5.1）
Python （3.8、3.9、3.10、3.11、3.12、3.13）
我们强烈推荐并仅正式支持 每个 Python 和 Django 系列。

以下软件包是可选的：

PyYAML， uritemplate （5.1+， 3.0.0+） - 架构生成支持。
Markdown （3.3.0+） - Markdown 对可浏览 API 的支持。
Pygments （2.7.0+） - 为 Markdown 处理添加语法高亮显示。
django-filter （1.0.1+） - 过滤支持。
django-guardian （1.1.1+） - 对象级权限支持。

安装

使用 安装 ，包括您想要的任何可选软件包...pip
```
pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support
```
### 序列化器的定义与使用

序列化也叫序列化器，是指把查询集或者模型类实例这种django的数据类型转化为json或者xml

转化为方便前端可以轻松渲染的json/xml/yaml

所以序列化和反序列化是为了前后端数据交互

tutorial/app_name/serializers.py用于我们的数据表示。

序列化的过程中，会根据类中定义的序列化类的字段进行序列化输出。不定义则不会输出

如果默认的序列化输出无法满足我们的需求，那么可以重写 to_representation() 改变序列化的输出。如上所示，显示班级的指定信息。

如果使用PrimaryKeyRelatedField 此字段将被序列化为关联对象的主键

序列化器可以把模型对象转换成字典，经过response以后编程json字符串

反序列化是把客户端发过来的数据经过request之后变成字典，序列化器可以把字典转换成模型，

反序列化可以完成数据校验功能

```py
from rest_framework import serializers
from .models import Group, User



class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

```

下表来源
https://www.cnblogs.com/x945669/p/13307795.html

常用字段类型：
|||
|:-:|:-:|
|字段|	字段构造方式|
|BooleanField|	BooleanField()|
|NullBooleanField|	NullBooleanField()|
|CharField|	CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)|
|EmailField|	EmailField(max_length=None, min_length=None, allow_blank=False)|
|RegexField|	RegexField(regex, max_length=None, min_length=None, allow_blank=False)|
|SlugField|	SlugField(maxlength=50, min_length=None, allow_blank=False) 正则字段，验证正则模式 [a-zA-Z0-9-]+|
|URLField|	URLField(max_length=200, min_length=None, allow_blank=False)|
|UUIDField|	UUIDField(format=’hex_verbose’) format: 1) 'hex_verbose' 如"5ce0e9a5-5ffa-654b-cee0-1238041fb31a" 2） 'hex' 如 "5ce0e9a55ffa654bcee01238041fb31a" 3）'int' - 如: "123456789012312313134124512351145145114" 4）'urn' 如: "urn:uuid:5ce0e9a5-5ffa-654b-cee0-1238041fb31a"|
|IPAddressField|	IPAddressField(protocol=’both’, unpack_ipv4=False, **options)|
|IntegerField|	IntegerField(max_value=None, min_value=None)|
|FloatField|	FloatField(max_value=None, min_value=None)|
|DecimalField|	DecimalField(max_digits, decimal_places, coerce_to_string=None, max_value=None, min_value=None) max_digits: 最多位数 decimal_palces: 小数点位置|
|DateTimeField|	DateTimeField(format=api_settings.DATETIME_FORMAT, input_formats=None)|
|DateField|	DateField(format=api_settings.DATE_FORMAT, input_formats=None)|
|TimeField|	TimeField(format=api_settings.TIME_FORMAT, input_formats=None)|
|DurationField|	DurationField()|
|ChoiceField|	ChoiceField(choices) choices与Django的用法相同|
|MultipleChoiceField|	MultipleChoiceField(choices)|
|FileField|	FileField(max_length=None, allow_empty_file=False, use_url=UPLOADED_FILES_USE_URL)|
|ImageField|	ImageField(max_length=None, allow_empty_file=False, use_url=UPLOADED_FILES_USE_URL)|
|ListField|	ListField(child=, min_length=None, max_length=None)|
|DictField|	DictField(child=)|

选项参数：
|参数名称|	作用|
|:-:|:-:|
|max_length|	最大长度|
|min_lenght|	最小长度|
|allow_blank|	是否允许为空|
|trim_whitespace|	是否截断空白字符|
|max_value|	最小值|
|min_value|	最大值

通用参数：

|参数名称|	说明|
|:-:|:-:|
|read_only|	表明该字段仅用于序列化输出，默认False|
|write_only|	表明该字段仅用于反序列化输入，默认False|
|required|	表明该字段在反序列化时必须输入，默认True|
|default|	反序列化时使用的默认值|
|allow_null|	表明该字段是否允许传入None，默认False|
|validators|	该字段使用的验证器|
|error_messages|	包含错误编号与错误信息的字典|
|label|	用于HTML展示API页面时，显示的字段名称|
|help_text|	用于HTML展示API页面时，显示的字段帮助提示信息|


在视图中添加序列化器

为什么使用  ViewSet ？
 
减少重复代码：每个  ModelViewSet  自动提供  list / create / retrieve / update / destroy  操作。
 
统一路由配置：配合  DRF  的  Router ，自动生成标准 REST 路由（如  ）。
 
可扩展性：可通过重写方法（如  perform_create ）添加自定义逻辑。

```py
from tutorial.quickstart.serializers import GroupSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
```

如何扩展功能？
 
自定义动作：添加  @action  装饰器实现特殊端点：
```py
class DroneViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """自定义动作：激活无人机"""
        drone = self.get_object()
        drone.activate()
        return Response({"status": "activated"})
```


进行路由配置

好了，现在让我们连接 API URL。继续 ...tutorial/urls.py
```py
from django.urls import include, path
from rest_framework import routers

from tutorial.quickstart import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
```

因为我们使用的是视图集而不是视图，所以我们可以通过简单地将视图集注册到 router 类来自动生成 API 的 URL conf。

同样，如果我们需要对 API URL 进行更多控制，我们可以简单地简化为使用常规的基于类的视图，并显式编写 URL conf。

最后，我们包括了默认的登录和注销视图，以便与可浏览的 API 一起使用。这是可选的，但如果您的 API 需要身份验证并且您想要使用可浏览的 API，则这很有用。

分页
分页允许您控制每页返回的对象数。要启用它，请将以下行添加到tutorial/settings.py
```py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}
```
设置
搭。设置模块将位于'rest_framework'INSTALLED_APPStutorial/settings.py
```py
INSTALLED_APPS = [
    ...
    'rest_framework',
]
```

### 测试我们的 API
现在，我们已准备好测试我们构建的 API。让我们从命令行启动服务器。

python manage.py runserver
我们现在可以从命令行访问我们的 API，使用如下工具......curl
```sh
bash: curl -u admin -H 'Accept: application/json; indent=4' http://127.0.0.1:8000/users/
Enter host password for user 'admin':
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "url": "http://127.0.0.1:8000/users/1/",
            "username": "admin",
            "email": "admin@example.com",
            "groups": []
        }
    ]
}
```
或者使用 httpie、命令行工具...
```sh
bash: http -a admin http://127.0.0.1:8000/users/
http: password for admin@127.0.0.1:8000:: 
$HTTP/1.1 200 OK
...
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "email": "admin@example.com",
            "groups": [],
            "url": "http://127.0.0.1:8000/users/1/",
            "username": "admin"
        }
    ]
}
```
或者直接通过浏览器，通过访问 URL ...http://127.0.0.1:8000/users/


### 跨域问题
```
pip install django-cors-headers

修改设置
修改Django项目文件夹下的 setting.py 文件
代码语言：javascript代码运行次数：0
复制

Cloud Studio
代码运行
# 记得修改允许访问的IP
ALLOWED_HOSTS = ['*'] # 允许全部IP访问项目
代码语言：javascript代码运行次数：0
复制

Cloud Studio
代码运行
# setting.py 修改以下内容
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders', # 注册app corsheaders
    'app01',# 你的app
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # 加入中间键 位置必须在这里 不能在其他位置
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware', 如果你的项目没有考虑到 csrf 网络攻击,可注释掉,否则会报错没有传递 csrf cookie
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
代码语言：javascript代码运行次数：0
复制

Cloud Studio
代码运行
# 在 setting.py 末尾添加以下设置
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ('*')

配置完以上内容后Django就可用跨域访问啦！基本需求就已经解决啦
```

### vue 利用axios发送请求

npm install axios




### djaong WebSocket
```
# 安装必要依赖
pip install daphne

# 使用ASGI服务器启动（必须）
daphne your_project.asgi:application --port 8000

# 或者开发模式（需确认settings配置正确）
python manage.py runserver --noreload
```
### redis
pip install django-redis


### 结合：

https://zhuanlan.zhihu.com/p/25080236

cd frontend
npm install
npm run build


创建dist



. 使用Django的通用视图 TemplateView
找到项目根 urls.py (即ulb_manager/urls.py)，使用通用视图创建最简单的模板控制器，访问 『/』时直接返回 index.html


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    **url(r'^$', TemplateView.as_view(template_name="index.html")),**
    url(r'^api/', include('backend.urls', namespace='api'))
]

6. 配置Django项目的模板搜索路径
上一步使用了Django的模板系统，所以需要配置一下模板使Django知道从哪里找到index.html

打开 settings.py (ulb_manager/settings.py)，找到TEMPLATES配置项，修改如下:


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        **'DIRS': ['frontend/dist']**,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
注意这里的 frontend 是VueJS项目目录，dist则是运行 npm run build 构建出的index.html与静态文件夹 static 的父级目录

这时启动Django项目，访问 / 则可以访问index.html，但是还有问题，静态文件都是404错误，下一步我们解决这个问题

7. 配置静态文件搜索路径
打开 settings.py (ulb_manager/settings.py)，找到 STATICFILES_DIRS 配置项，配置如下:


# Add for vuejs
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/dist/static"),
]
这样Django不仅可以将/ulb 映射到index.html，而且还可以顺利找到静态文件

此时访问 /ulb 我们可以看到使用Django作为后端的VueJS helloworld

ALL DONE.



8. 开发环境
因为我们使用了Django作为后端，每次修改了前端之后都要重新构建（你可以理解为不编译不能运行）

除了使用Django作为后端，我们还可以在dist目录下面运行以下命令来看效果：

