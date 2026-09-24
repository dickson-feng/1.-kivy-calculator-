name: Build APK
on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu‑latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup‑python@v5
        with:
          python‑version: "3.11"

      - name: Install system dependencies
        run: |
          sudo apt‑get update
          sudo apt‑get install ‑y git zip unzip openjdk‑17‑jdk autoconf libtool pkg‑config zlib1g‑dev libncurses‑dev cmake libffi‑dev libssl‑dev

      - name: Install buildozer
        run: |
          python3 ‑m venv venv
          source venv/bin/activate
          pip install buildozer cython

      - name: Build APK
        run: |
          source venv/bin/activate
          buildozer android debug

      - name: Upload APK artifact
        uses: actions/upload‑artifact@v4
        with:
          name: calculator‑apk
          path: bin/*.apk
