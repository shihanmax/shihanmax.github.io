# !/bin/bash
bundle exec jekyll build
bundle exec jekyll serve --host 0.0.0.0 --port 80 --watch --force_polling --incremental
