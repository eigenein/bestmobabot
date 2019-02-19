#!/usr/bin/env bash
curl 'https://heroes.cdnvideo.ru/vk/v0479/locale/ru.json.gz' --output bestmobabot/js/ru.json.gz
curl 'https://heroes.cdnvideo.ru/vk/v0481/lib/lib.json.gz' --output bestmobabot/js/lib.json.gz
curl 'https://heroes.cdnvideo.ru/vk/v0481/assets/heroes.js' --output bestmobabot/js/heroes.js
curl 'https://heroes.cdnvideo.ru/vk/v0481/assets/hx/skills.sc?js=1' --output bestmobabot/js/skills.sc
