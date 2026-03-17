# JSON Schema Reference

The parser outputs JSON validated against `sms-backup-restore.schema.json` (JSON Schema draft-07), located in the project root. The schema is the source of truth for field names, types, and enum semantics.

All values are strings extracted directly from XML attributes unless otherwise noted. The `date_iso` field on each record type is computed by the parser (not present in the original XML).

Combined output files contain top-level `sms`, `mms`, and `calls` arrays. Per-type output files contain a single top-level array of the relevant record type.

`additionalProperties` is `true` on individual records, so fields not listed below may appear if present in the source XML.

## SMS Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocol` | string | No | Transport protocol identifier. Almost always `"0"`. |
| `address` | string | **Yes** | Phone number of sender or recipient. |
| `date` | string | **Yes** | Timestamp as Java epoch milliseconds. |
| `date_iso` | string (date-time) | No | Computed ISO 8601 UTC timestamp from `date`. Injected by parser. |
| `type` | string | **Yes** | Message direction/status. See [SMS Type Enum](#sms-type). |
| `subject` | string or null | No | Subject line. Almost always `"null"` for SMS. |
| `body` | string | **Yes** | Full text content of the message. |
| `toa` | string or null | No | Type of Address for destination. |
| `sc_toa` | string or null | No | Type of Address for service center. |
| `service_center` | string or null | No | SMSC number that routed the message. |
| `read` | string | **Yes** | Read status. `"0"` = Unread, `"1"` = Read. |
| `status` | string | **Yes** | Delivery status. See [SMS Status Enum](#sms-status). |
| `locked` | string | No | Lock status. `"0"` = Unlocked, `"1"` = Locked. |
| `date_sent` | string | No | Send timestamp in Java epoch ms. May be `"0"`. |
| `sub_id` | string | No | SIM subscription ID. |
| `readable_date` | string | No | Human-readable date (if backup preference enabled). |
| `contact_name` | string | No | Contact display name (if backup preference enabled). |

## MMS Fields

MMS records include flat attributes plus nested `parts` and `addrs` arrays.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | **Yes** | Timestamp in Java epoch milliseconds. |
| `date_iso` | string (date-time) | No | Computed ISO 8601 UTC timestamp. Injected by parser. |
| `ct_t` | string | **Yes** | Top-level Content-Type of the MMS. |
| `msg_box` | string | **Yes** | Mailbox folder. See [MMS Msg Box Enum](#mms-msg-box). |
| `rr` | string | **Yes** | Read report request flag. |
| `sub` | string | No | Subject line. |
| `read_status` | string | **Yes** | Read status in MMS protocol sense. |
| `address` | string | **Yes** | Primary sender or recipient phone number. |
| `m_id` | string | **Yes** | Globally unique Message-ID from MMS service center. |
| `read` | string | **Yes** | User read status. `"0"` = Unread, `"1"` = Read. |
| `m_size` | string | **Yes** | Message size in bytes. |
| `m_type` | string | **Yes** | MMS message type code (e.g., `"128"` = Send Request, `"132"` = Retrieve Confirmation). |
| `text_only` | string | No | `"0"` = Has media, `"1"` = Text only. |
| `seen` | string | **Yes** | Notification seen status. `"0"` = Not seen, `"1"` = Seen. |
| `v` | string | **Yes** | MMS spec version number. |
| `exp` | string | **Yes** | Expiry duration/timestamp in seconds. |
| `pri` | string | **Yes** | Priority. `"128"` = Normal, `"129"` = High, `"130"` = Low. |
| `locked` | string | **Yes** | Lock status. `"0"` = Unlocked, `"1"` = Locked. |
| `date_sent` | string | **Yes** | Send timestamp in Java epoch ms. |
| `tr_id` | string | **Yes** | Transaction ID for MMS protocol correlation. |
| `m_cls` | string | **Yes** | Message class (`"personal"`, `"advertisement"`, etc.). |
| `d_rpt` | string | **Yes** | Delivery report request flag. |
| `st` | string | **Yes** | MMS delivery status. |
| `retr_st` | string | **Yes** | Retrieval status from MMS server. |
| `ct_cls` | string | **Yes** | Content class. |
| `ct_l` | string | **Yes** | Content-Location URI. |
| `sub_cs` | string | **Yes** | Character set for subject field. |
| `d_tm` | string | **Yes** | Delivery time. |
| `retr_txt_cs` | string | **Yes** | Character set for retrieval text. |
| `resp_txt` | string | **Yes** | Response text from MMS server. |
| `rpt_a` | string | **Yes** | Report allowed flag. |
| `retr_txt` | string | **Yes** | Retrieval text from MMS server. |
| `resp_st` | string | **Yes** | Response status code from MMS server. |
| `sim_slot` | string | No | SIM card slot identifier. |
| `readable_date` | string | No | Human-readable date (if backup preference enabled). |
| `contact_name` | string | No | Contact display name (if backup preference enabled). |

### MMS Parts

Each MMS record contains a `parts` array of message components (text, images, audio, video, SMIL).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `seq` | string | **Yes** | Sequence number controlling part order. |
| `ct` | string | **Yes** | MIME content type (e.g., `"text/plain"`, `"image/jpeg"`). |
| `name` | string | **Yes** | Part name, often from original filename. |
| `chset` | string | **Yes** | Character set (IANA number, e.g., `"106"` = UTF-8). |
| `cd` | string | **Yes** | Content-Disposition header value. |
| `fn` | string | **Yes** | Filename from content headers. |
| `cid` | string | **Yes** | Content-ID for referencing from SMIL. |
| `cl` | string | **Yes** | Content-Location identifier. |
| `ctt_s` | string | **Yes** | Content-Type start parameter. |
| `ctt_t` | string | **Yes** | Content-Type type parameter. |
| `text` | string | **Yes** | Text content for text parts; `"null"` for binary parts. |
| `data` | string | No | Base64-encoded binary payload. Omitted with `--strip-media`. |

### MMS Addresses

Each MMS record contains an `addrs` array identifying conversation participants.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `address` | string | **Yes** | Phone number or email of participant. |
| `type` | string | **Yes** | Participant role. See [MMS Address Type Enum](#mms-address-type). |
| `charset` | string | **Yes** | Character set identifier. |

## Call Log Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `number` | string | **Yes** | Phone number associated with the call. |
| `duration` | string | **Yes** | Call length in seconds. `"0"` for missed/rejected. |
| `date` | string | **Yes** | Timestamp in Java epoch milliseconds. |
| `date_iso` | string (date-time) | No | Computed ISO 8601 UTC timestamp. Injected by parser. |
| `type` | string | **Yes** | Call direction/disposition. See [Call Type Enum](#call-type). |
| `presentation` | string | **Yes** | Caller ID presentation. See [Call Presentation Enum](#call-presentation). |
| `subscription_id` | string | No | SIM subscription that handled the call. |
| `readable_date` | string | No | Human-readable date (if backup preference enabled). |
| `contact_name` | string | No | Contact display name (if backup preference enabled). |

## Enum Reference

### SMS Type

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |
| `5` | Failed |
| `6` | Queued |

### SMS Status

| Value | Meaning |
|-------|---------|
| `-1` | None |
| `0` | Complete |
| `32` | Pending |
| `64` | Failed |

### MMS Msg Box

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |

### MMS Address Type

| Value | Meaning |
|-------|---------|
| `129` | BCC |
| `130` | CC |
| `137` | From |
| `151` | To |

### Call Type

| Value | Meaning |
|-------|---------|
| `1` | Incoming |
| `2` | Outgoing |
| `3` | Missed |
| `4` | Voicemail |
| `5` | Rejected |
| `6` | Refused List |

### Call Presentation

| Value | Meaning |
|-------|---------|
| `1` | Allowed |
| `2` | Restricted |
| `3` | Unknown |
| `4` | Payphone |
