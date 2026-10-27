[app]
title = Calculator
package.name = calculator
package.domain = org.simple.calculator
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_patterns = gen_assets.py,test_calculator.py,README.md,build_apk_colab.ipynb,calculator.zip
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
icon.filename = icon.png
presplash.filename = presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
