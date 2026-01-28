# 日本語化
FROM postgres
RUN  apt-get update && apt-get upgrade -y \
  && apt-get install -y locales \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && localedef -i ja_JP -c -f UTF-8 -A /usr/share/locale/locale.alias ja_JP.UTF-8 \
  && LANG=ja_JP.UTF-8 && LANGUAGE=ja_JP:ja \
  && locale
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja

