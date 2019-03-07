#!/usr/bin/env bash
curl 'https://heroes.cdnvideo.ru/vk/v0488/locale/ru.json.gz?js=1' --output bestmobabot/js/ru.json.gz
curl 'https://heroes.cdnvideo.ru/vk/v0488/lib/lib.json.gz?js=1' --output bestmobabot/js/lib.json.gz
curl 'https://heroes.cdnvideo.ru/vk/v0488/assets/heroes.js' --output bestmobabot/js/heroes.js
curl 'https://heroes.cdnvideo.ru/vk/v0488/assets/hx/skills.sc?js=1' --output bestmobabot/js/skills.sc
