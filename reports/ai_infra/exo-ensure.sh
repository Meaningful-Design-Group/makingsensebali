#!/bin/zsh
# exo-ensure.sh — installed on the Mac mini as a launchd LaunchAgent
# (com.fabcity.exo-ensure), runs at login + every 5 min.
#
# Guarantees the reporter's vision model (Gemma-4 e4b) is actually SERVING on
# the exo cluster. Pings the model; if it can't answer (missing, unloaded, or
# a "ghost" instance left behind when the MacBook node leaves the cluster) it
# clears stale e4b instances and re-places. With only the mini present (MacBook
# taken away) the re-place lands on the mini, which has the weights cached, so
# the reporter self-heals. Gemini fallback covers the brief gap.
M="mlx-community/gemma-4-e4b-it-6bit"
/usr/bin/open -a EXO 2>/dev/null
for i in $(seq 1 30); do /usr/bin/curl -sf -m 3 http://localhost:52415/v1/models >/dev/null 2>&1 && break; sleep 2; done
if /usr/bin/curl -sf -m 30 http://localhost:52415/v1/chat/completions -H 'Content-Type: application/json' \
   -d "{\"model\":\"$M\",\"max_tokens\":1,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" >/dev/null 2>&1; then
  exit 0
fi
for iid in $(/usr/bin/curl -sf -m 5 http://localhost:52415/state | /usr/bin/python3 -c "import sys,json;d=json.load(sys.stdin);[print(k) for k,v in d.get('instances',{}).items() if 'gemma-4-e4b' in str(v)]" 2>/dev/null); do
  /usr/bin/curl -sf -m 10 -X DELETE "http://localhost:52415/instance/$iid" >/dev/null 2>&1
done
sleep 2
/usr/bin/curl -sf -m 25 -X POST http://localhost:52415/place_instance -H 'Content-Type: application/json' \
   -d "{\"model_id\":\"$M\",\"min_nodes\":1}" >/dev/null 2>&1
echo "$(date) e4b not serving -> cleared + re-placed" >> /tmp/exo-ensure.log
