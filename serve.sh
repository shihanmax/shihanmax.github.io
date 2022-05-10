# !/bin/bash
bundle exec jekyll build --force_polling
bundle exec jekyll serve --host shihanmax.top --port 80 --watch --force_polling
