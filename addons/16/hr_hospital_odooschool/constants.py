import datetime

STATE_LIST = [
    ("draft", "Draft"),
    ("created", "Created"),
    ("done", "Done"),
]
DOCTOR_STATE_LIST = [
    ("draft", "Draft"),
    ("active", "Active"),
    ("arch", "Arch"),
]

SEX_LIST = [
    ('man', 'Man'),
    ('woman', 'Woman'),
    ('else', 'Else')
]

# Duration of one visit to doctor. -> hours, minutes, seconds.
VISIT_DURATION = datetime.timedelta(
    hours=00, minutes=30, seconds=00
)

# Duration of one doctor shift. -> hours, minutes, second.
WORK_SHIFT_DURATION = [
    ("3", '3 hour'),
    ("6", '6 hours'),
    ("8", '8 hours')
]

delta = datetime.timedelta(seconds=1)
