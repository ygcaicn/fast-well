## 200-299

{
    "code": 0
    "data": {}
    "msg": ""
}

code: 0 正常返回




## 422	Error: Unprocessable Entity
数据验证错误

{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": [
        "body",
        "grant_type"
      ],
      "msg": "String should match pattern 'password'",
      "input": "3",
      "ctx": {
        "pattern": "password"
      },
      "url": "https://errors.pydantic.dev/2.1/v/string_pattern_mismatch"
    }
  ]
}

## 400 Error: Bad Request

{
  "detail": "Invalid captcha"
}




在Axios中，以下情况会被认为是错误请求：

HTTP状态码不在200-299的范围内：Axios将非2xx的HTTP状态码视为错误请求。这包括常见的错误状态码如400（Bad Request）、401（Unauthorized）、403（Forbidden）、404（Not Found）等。

响应拦截器中手动抛出的错误：在响应拦截器中，如果您手动抛出一个错误（使用Promise.reject()），则Axios会将其视为错误请求。

网络错误：如果请求无法发送到服务器或无法接收到服务器的响应，Axios会将其视为错误请求。这可能是由于网络连接问题、服务器故障或其他网络相关问题引起的。
