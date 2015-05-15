#!/usr/bin/env python
"""
Created on Tue May 12 19:37:11 2015

@author: George Mack <dreambeamz@gmail.com>
"""

Notes = """
Spreadsheet1:  ColumnH  50% Refund -> Column{E,F} (email address) ->  (also grab row#)
Spreadsheet2: if Column H (OrderType) == "Eventbrite Completed": Column A (OrderNumber) -> Column I (Total Paid)

Output:
Order Number, Total Paid * 0.5      (<-and add to new columns in spreadsheet 1)
"""


import sys

file_name = sys.argv[1]
file_name2 = sys.argv[2]

keepers = set([
    "General Admission 18+",
    "Early Bird General Admission 18+",
    "VIP 18+ Findor Travel",
    "Early Bird VIP 18+",
    "VIP 18+",
    "General Admission 18+ Findor Travel",
])

with open(file_name) as fh:
    file_lines = [x.split("\t") for x in fh.read().split("\n")]

with open(file_name2) as fh2:
    file_lines2 = [x.split("\t") for x in fh2.read().split("\n")]

headers = file_lines[0]
file_lines = file_lines[1:]

headers2 = file_lines2[0]
file_lines2 = [x for x in file_lines2[1:] if len(x) > 6 and x[6] in keepers]

buyer_emails = [x[4].strip().lower() for x in file_lines]
confirm_emails = [x[5].strip().lower() for x in file_lines]

email_dict2 = {x[4]:x for x in file_lines2}

count = 0
dup_user_count = 0

you_suck = set()

def get_counts(email):
    if email in you_suck:
        return
    global count, line_count, dup_user_count
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
            dup_user_count += 1
        else:
            file_lines[be_lines[0]][9] = "Duplicates on lines {0} {1} ".format(
                [x + 2 for x in be_lines], [x + 2 for x in ce_lines]
                ) + file_lines[be_lines[0]][9]
        count += 1

for be, ce in zip(buyer_emails, confirm_emails):
    get_counts(be)
    if ce != be:
        get_counts(ce)

TO_BE_REFUNDED = []

for x in file_lines:
    emails = set(x[4:6])
    if x[7].strip().lower() == "50% refund" and \
    "eventbrite" in x[6].lower() and \
    not [y for y in emails if y not in you_suck] and \
    [y for y in emails if y in email_dict2]:
        email = [y for y in emails if y in email_dict2][0]
        z = email_dict2[email]
        value = (z[0], str(round(float(z[8]) * 0.5, 2)))
        TO_BE_REFUNDED.append(value)

print(count, "duplicate lines")
print(dup_user_count, "people typed in their email address wrong")
print(len(TO_BE_REFUNDED), "people are getting a refund")
print(round(sum(float(x[1]) for x in TO_BE_REFUNDED), 2), "dollars refunded")

# By cancellation credit option
canc_options = [x[7] for x in file_lines]
option_list = set(canc_options)
for option in sorted(option_list):
    print(option, canc_options.count(option))

file_lines.insert(0, headers)
file_lines = ["\t".join(x) for x in file_lines]

with open("result.tsv", "w") as fh:
    fh.write("\n".join(file_lines))

TO_BE_REFUNDED = ["\t".join(x) for x in TO_BE_REFUNDED]

with open("to-be-refunded.tsv", "w") as fh:
    fh.write("\n".join(TO_BE_REFUNDED))
