# 轮播图推荐数
BANNER_COUNT = 3

# 短信过期时间
SMS_EXP = 60
# 短信缓存的key
SMS_CACHE_KEY = 'sms_%s'

# 后台http根路径
# BASE_URL = 'http://127.0.0.1:8000'
BASE_URL = "https://example.com"

# 前台http根路径
# LUFFY_URL = 'http://127.0.0.1:8080'
LUFFY_URL = "http://localhost:8080"

# 订单支付成功的后台异步回调接口
NOTIFY_URL = BASE_URL + '/notify'

# 订单支付成功的前台同步回调接口
RETURN_URL = LUFFY_URL + '/user'
