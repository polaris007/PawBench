curl -X POST \
  https://wishub-x6.ctyun.cn/v1/chat/completions \
  -H 'Authorization: Bearer 1a37f951c55145fcaaed12bafea9b823' \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
  "model": "DeepSeek-V3-0324",
  "messages": [
    {
      "role": "user",
      "content": "你好"
    }
  ]
}'
