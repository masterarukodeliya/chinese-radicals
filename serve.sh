#!/bin/bash
# Держит локальный веб-сервер + cloudflare-туннель живыми, перезапускает при падении.
# URL пишется в url.txt рядом.
cd /home/agent/projects/chinese-radicals || exit 1
DIR=/home/agent/projects/chinese-radicals
CF=/tmp/cloudflared

# 1) локальный сервер (если не поднят)
if ! curl -s -o /dev/null http://127.0.0.1:8787/index.html; then
  nohup python3 -m http.server 8787 --bind 127.0.0.1 >/tmp/httpserver.log 2>&1 &
fi

# 2) туннель в бесконечном цикле с авто-перезапуском
while true; do
  "$CF" tunnel --url http://127.0.0.1:8787 --no-autoupdate >/tmp/cf.log 2>&1 &
  CFPID=$!
  # ждём появления URL и кладём в url.txt
  for i in $(seq 1 15); do
    U=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf.log | head -1)
    [ -n "$U" ] && echo "$U" > "$DIR/url.txt" && break
    sleep 1
  done
  wait $CFPID   # если cloudflared упадёт — цикл перезапустит
  sleep 2
done
