"""Constants and enum lookup tables for SMS Backup & Restore record types."""

SMS_TYPES = {
    "1": "Received",
    "2": "Sent",
    "3": "Draft",
    "4": "Outbox",
    "5": "Failed",
    "6": "Queued",
}

MMS_MSG_BOX = {
    "1": "Received",
    "2": "Sent",
    "3": "Draft",
    "4": "Outbox",
}

CALL_TYPES = {
    "1": "Incoming",
    "2": "Outgoing",
    "3": "Missed",
    "4": "Voicemail",
    "5": "Rejected",
    "6": "Refused List",
}

ADDR_TYPES = {
    "129": "BCC",
    "130": "CC",
    "137": "From",
    "151": "To",
}

PRESENTATION_TYPES = {
    "1": "Allowed",
    "2": "Restricted",
    "3": "Unknown",
    "4": "Payphone",
}

SMS_STATUS = {
    "-1": "None",
    "0": "Complete",
    "32": "Pending",
    "64": "Failed",
}
