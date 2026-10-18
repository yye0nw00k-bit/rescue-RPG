[app]
title = 천상 키우기
package.name = chunsangraising
package.domain = org.yeonwook
source.dir = .
source.include_exts = py,kv,json,png,jpg,atlas,ttf,otf,txt
version = 1.0.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1
android.permissions = INTERNET
android.accept_sdk_license = True
p4a.bootstrap = sdl2
p4a.local_recipes = ./p4a-recipes

# Android build settings
android.api = 36
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
