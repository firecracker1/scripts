#!/usr/bin/env python
"""
Created on Tue May 12 19:37:11 2015

@author: George Mack <dreambeamz@gmail.com>
"""

import sys

file_name = sys.argv[1]

with open(file_name) as fh:
    file_lines = [x.split("\t") for x in fh.read().split("\n")]

headers = file_lines[0]
file_lines = file_lines[1:]

buyer_emails = [x[4].strip().lower() for x in file_lines]
confirm_emails = [x[5].strip().lower() for x in file_lines]
count = 0
idiot_count = 0

you_suck = set()

def get_counts(email):
    if email in you_suck:
        return
    global count, line_count, idiot_count
    be_count = buyer_emails.count(email)
    ce_count = confirm_emails.count(email)
    if be_count > 1 or ce_count > 1:
        be_lines = [
            x for x, y in
            zip(range(len(buyer_emails)), buyer_emails)
            if y == email
            ]
        ce_lines = [
            x for x, y in
            zip(range(len(confirm_emails)), confirm_emails)
            if y == email
            ]
        be_lines.sort()
        ce_lines.sort()
        you_suck.add(email)
        if be_lines != ce_lines:
            print(email, be_lines, ce_lines)
            idiot_count += 1
        else:
            file_lines[be_lines[0]][9] = "Duplicates on lines {0} {1} ".format(
                [x + 2 for x in be_lines], [x + 2 for x in ce_lines]
                ) + file_lines[be_lines[0]][9]
        count += 1

for be, ce in zip(buyer_emails, confirm_emails):
    get_counts(be)
    if ce != be:
        get_counts(ce)

print(count, "people are bastards")
print(idiot_count, "people are idiots")

file_lines.insert(0, headers)
file_lines = ["\t".join(x) for x in file_lines]

with open("result.tsv", "w") as fh:
    fh.write("\n".join(file_lines))
