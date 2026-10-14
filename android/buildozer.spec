[app]
title = 태현이 구하기(?)
package.name = taehyunrescue
package.domain = org.yeonwook
source.dir = .
source.include_exts = py,kv,json,png,jpg,atlas
version = 1.0.0
requirements = python3,kivy
orientation = landscape
fullscreen = 1

# Android build settings
android.api = 36
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
