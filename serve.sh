# !/bin/bash
bundle exec jekyll build --force_polling
bundle exec jekyll serve --host 0.0.0.0 --port 80 --watch --force_polling
