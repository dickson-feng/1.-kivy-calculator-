[app]
package.name = calculator
package.domain = org.calculator
source.dir = .
source.include_exts = py,png,jpg
source.main = main.py
package.version = 0.1
requirements = python3,kivy

android.minapi = 24
android.api = 32
android.ndk = 25c
android.archs = arm64-v8a
android.accept_sdk_license = True
android.androidx = True
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

log_level = 2
orientation = portrait
