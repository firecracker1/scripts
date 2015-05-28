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
file_lines2 = [x for x in file_lines2[1:]
    if len(x) > 6 and x[6] in keepers and
    x[7].strip() == "Eventbrite Completed"]

buyer_emails = [x[4].strip().lower() for x in file_lines]
confirm_emails = [x[5].strip().lower() for x in file_lines]

email_dict2 = {x[4].strip().lower():x for x in file_lines2}

incorrect_emails = []
dup_users = set()

def get_counts(email):
    if email in dup_users:
        return
    global count, line_count
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
        dup_users.add(email)
        if be_lines != ce_lines:
            incorrect_emails.append((email, be_lines, ce_lines))
        else:
            file_lines[be_lines[0]][9] = "Duplicates on lines {0} {1} ".format(
                [x + 2 for x in be_lines], [x + 2 for x in ce_lines]
                ) + file_lines[be_lines[0]][9]

for be, ce in zip(buyer_emails, confirm_emails):
    get_counts(be)
    if ce != be:
        get_counts(ce)

TO_BE_REFUNDED = []
NOT_REFUNDING_COUNT = 0
NOT_PURCHASED_FROM_EB_COUNT = 0
WAS_DUPLICATE_COUNT = 0
NOT_IN_SPREADSHEET2_COUNT = 0

for x in file_lines:
    emails = set(a.strip().lower() for a in x[4:6])
    if x[7].strip().lower() == "50% refund":
        was_purchased_from_eb = "eventbrite" in x[6].lower()
        was_not_dup = not not [y for y in emails if y not in dup_users]
        was_in_spreadsheet2 = not not [y for y in emails if y in email_dict2]
        all_reqs = [was_purchased_from_eb, was_not_dup, was_in_spreadsheet2]
        if all(all_reqs):
            email = [y for y in emails if y in email_dict2][0]
            z = email_dict2[email]
            value = (z[0], str(round(float(z[8]) * 0.5, 2)))
            TO_BE_REFUNDED.append(value)
            dollar_val = "${0} auto sent".format(value[1])
            if x[8].strip():
                x[8] = " // ".join([dollar_val, x[8]])
            else:
                x[8] = dollar_val
        else:
            NOT_REFUNDING_COUNT += 1
            if not was_purchased_from_eb:
                NOT_PURCHASED_FROM_EB_COUNT += 1
            if not was_not_dup:
                WAS_DUPLICATE_COUNT += 1
            if not was_in_spreadsheet2:
                NOT_IN_SPREADSHEET2_COUNT += 1


print("\nRefund stats:")
print("* {0} Requested refund but not eligible "
    "for a refund".format(NOT_REFUNDING_COUNT))
print("* {0} Requested refund but did not purchase from "
    "Eventbrite".format(NOT_PURCHASED_FROM_EB_COUNT))
print("* {0} Requested refund, but submitted multiple "
    "requests".format(WAS_DUPLICATE_COUNT))
print("* {0} Requested refund, but was not in "
    "spreadsheet 2 (or order type was not "
    "'Eventbrite Completed' or ticket type not in "
    "{1})".format(NOT_IN_SPREADSHEET2_COUNT, keepers))
print("* {0} people are getting a refund".format(len(TO_BE_REFUNDED)))
print("* ${0} refunded".format(
    round(sum(float(x[1]) for x in TO_BE_REFUNDED), 2)))
print("\nOther stats:")
print("* {0} people submitted multiple requests for "
    "a refund".format(len(dup_users)))
print("* {0} people typed in their email address "
    "incorrectly".format(len(incorrect_emails)))


# By cancellation credit option
canc_options = [x[7] for x in file_lines]
option_list = set(canc_options)
for option in sorted(option_list):
    print("* {0} users chose cancellation option '{1}'".format(
        canc_options.count(option), option))

print("\n")

file_lines.insert(0, headers)
file_lines = ["\t".join(x) for x in file_lines]

with open("result.tsv", "w") as fh:
    print("Creating {0}".format(fh.name))
    fh.write("\n".join(file_lines))

TO_BE_REFUNDED = ["\t".join(x) for x in TO_BE_REFUNDED]

with open("to-be-refunded.tsv", "w") as fh:
    print("Creating {0}".format(fh.name))
    fh.write("\n".join(TO_BE_REFUNDED))
