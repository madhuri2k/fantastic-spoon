#!/usr/bin/env python3

import random
import rfeed


def truncate(s, n):
    x = len(s)
    if x > n and n > 2:
        s = ''.join([s[:(n-3)], '...'])
    return s

rss_len=10
title_len = 20

selec = random.sample(open('data.txt').readlines(), rss_len)
print("Selected {} items.".format(len(selec)))

content_list = []

for it in selec:
    it = it.strip()
    fi = rfeed.Item( title = truncate(it, title_len), description = it )
    content_list.append(fi)

feed = rfeed.Feed(
    title = "Sample RSS Feed",
    link = "https://github.com/madhuri2k/fantastic-spoon/random-rss",
    description = "A Random selection of items",
    language = "en-US",
    items = content_list)

print("Feed is {}".format(feed.rss()))


