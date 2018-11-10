#!/usr/bin/python
# -*- coding: utf-8 -*-
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
import base64, requests, urllib

PUBLIC_BEGIN = "-----BEGIN PUBLIC KEY-----\n"
PUBLIC_END = "\n-----END PUBLIC KEY-----"
PRIVATE_BEGIN = "-----BEGIN RSA PRIVATE KEY-----\n"
PRIVATE_END = "\n-----END RSA PRIVATE KEY-----"

# 验证是否是支付宝发来的通知链接地址
ALIPAY_REMOTE_ORIGIN_URL = 'https://mapi.alipay.com/gateway.do'

def param_str(params, q = '"'):
    """生成排序后待签名的字符串"""
    # 参数排序
    key_sorted = sorted(params.keys())
    content = ''
    # 拼接参数字符串
    for key in key_sorted:
        if params[key] is not '':
            content += key + '=' + q + params[key] + q + '&'
    content = content[:-1]
    return content

def sign(content, rsa_private):
    """
    rsa使用私钥签名
    :param content: 待签名的字符串
    :param rsa_private: 无头尾的私钥
    """
    private_key = RSA.importKey(PRIVATE_BEGIN + rsa_private + PRIVATE_END)
    hash_obj    = SHA.new(content)
    signer      = PKCS1_v1_5.new(private_key)
    result      = base64.b64encode(signer.sign(hash_obj))
    return result

def verify_sign(content, signstr, public_key):
    """
    rsa使用公钥验证签名
    :param content: 原始字符串
    :param signstr: 签名字符串
    :param public_key: 无头尾的公钥
    """
    try:
        public_key = RSA.importKey(PUBLIC_BEGIN + public_key + PUBLIC_END)
        hash_obj = SHA.new(content)
        verifier = PKCS1_v1_5.new(public_key)

        # 支付宝返回的 sign 经过 base64 encode，先 decode 一下
        signstr = base64.decodestring(signstr)
        return verifier.verify(hash_obj, signstr)
    except Exception:
        import traceback
        traceback.print_exc()

def moving_signed_order_str(ras_privte, partner, seller_id, order_num, subject, body, price, notify_url):
    """移动支付生成订单请求字符串"""
    orderdata = {
        "partner": partner,                  # 签约合作者身份ID
        "seller_id": seller_id,              # 签约卖家支付宝账号
        "out_trade_no": order_num,           # 商户网站唯一订单号
        "subject": subject,                  # 商品名称
        "body": body,                        # 商品详情
        "total_fee": price,                  # 商品金额
        "notify_url": notify_url,            # 服务器异步通知页面路径
        "service": "mobile.securitypay.pay", # 服务接口名称， 固定值
        "payment_type": "1",                 # 支付类型， 固定值
        "_input_charset": "utf-8",           # 参数编码， 固定值
        "it_b_pay": "30m",                   # 设置未付款交易的超时时间
        "return_url": "m.alipay.com",        # 支付宝处理完请求后，当前页面跳转到商户指定页面的路径，可空
    }

    # 待签名的字符串
    content = param_str(orderdata).encode("utf-8")
    # 签名后的字符串
    result = sign(content, ras_privte)
    # 请求字符串
    result = content + '&sign="' + urllib.quote(result) + '"&sign_type="RSA"'
    return result

def moving_verify_sign(params, public_key):
    """
    移动支付验证支付包的签名
    :param params: 请求参数
    :param public_key: 无头尾的公钥
    """
    sign_type  = params.pop("sign_type")
    signstr = params.pop("sign")
    content    = param_str(params, '')
    if sign_type.upper() == 'RSA':
        return verify_sign(content, signstr, public_key)

def verify_aplipay(partner, notify_id):
    """验证是否是支付宝发来的通知
    :param partner:   request.POST["seller_id"]，也可以 hardcode
    :param notify_id: request.POST["notify_id"]
    """
    payload = {'service':'notify_verify', 'partner':partner, 'notify_id':notify_id}
    r = requests.get(ALIPAY_REMOTE_ORIGIN_URL, params=payload)
    result = r.text
    print(result)
    if result.upper() == "TRUE":
        return True
    return False
