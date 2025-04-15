# 工作进程数
workers = 4

# 绑定地址和端口
bind = '127.0.0.1:8080'

# 工作模式
worker_class = 'sync'

# 超时时间
timeout = 120

# 访问日志和错误日志
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'

# 增加调试信息
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

# 确保工作进程能够正确启动
preload_app = True
reload = True 