# SMS Backup & Restore Parser — Technical Specification

| **Attribute** | **Value** |
|---------------|-----------|
| Project Name | SMS Backup & Restore Parser |
| Project Slug | `sms-backup-restore-parser` |
| Repository | [github.com/shruggietech/sms-backup-restore-parser](https://github.com/shruggietech/sms-backup-restore-parser) |
| License | [Apache License v2.0](https://www.apache.org/licenses/LICENSE-2.0) |
| Version | 0.1.0 |
| Author | William Thompson (ShruggieTech LLC) |
| Latest Revision Date | 2026-03-17 |
| Document Status | v0.1.0 |
| Audience | AI-first, Human-second |

<a name="table-of-contents" id="table-of-contents"></a>
<hr class="print-page-break">

## Table of Contents

- [1. Document Information](#1-document-information)
  - [1.1. Purpose and Audience](#11-purpose-and-audience)
  - [1.2. Scope](#12-scope)
  - [1.3. Document Maintenance](#13-document-maintenance)
  - [1.4. Conventions Used in This Document](#14-conventions-used-in-this-document)
  - [1.5. Terminology](#15-terminology)
  - [1.6. Reference Documents](#16-reference-documents)
- [2. Project Overview](#2-project-overview)
  - [2.1. Project Identity](#21-project-identity)
  - [2.2. Design Goals](#22-design-goals)
  - [2.3. Non-Goals](#23-non-goals)
  - [2.4. Platform and Runtime Requirements](#24-platform-and-runtime-requirements)
- [3. Upstream XML Format](#3-upstream-xml-format)
  - [3.1. File Structure](#31-file-structure)
  - [3.2. Structural Invariants](#32-structural-invariants)
- [4. SMS Fields](#4-sms-fields)
- [5. MMS Fields](#5-mms-fields)
  - [5.1. MMS Record Attributes](#51-mms-record-attributes)
  - [5.2. MMS Part Fields](#52-mms-part-fields)
  - [5.3. Common MMS Content Types](#53-common-mms-content-types)
  - [5.4. MMS Address Fields](#54-mms-address-fields)
- [6. Call Log Fields](#6-call-log-fields)
- [7. Enum Reference](#7-enum-reference)
  - [7.1. SMS Type](#71-sms-type)
  - [7.2. SMS Status](#72-sms-status)
  - [7.3. SMS/MMS Read](#73-smsmms-read)
  - [7.4. MMS Message Box](#74-mms-message-box)
  - [7.5. MMS Address Type](#75-mms-address-type)
  - [7.6. Call Type](#76-call-type)
  - [7.7. Call Presentation](#77-call-presentation)
- [8. Date Handling](#8-date-handling)
  - [8.1. Epoch Format](#81-epoch-format)
  - [8.2. Conversion](#82-conversion)
  - [8.3. date vs date_sent](#83-date-vs-date_sent)
  - [8.4. readable_date](#84-readable_date)
  - [8.5. Computed date_iso Field](#85-computed-date_iso-field)
- [9. XSD Known Issues](#9-xsd-known-issues)
  - [9.1. Missing Definitions](#91-missing-definitions)
  - [9.2. Type Mismatches](#92-type-mismatches)
  - [9.3. RCS and Advanced Messages](#93-rcs-and-advanced-messages)
  - [9.4. Backup Encryption](#94-backup-encryption)
- [10. Parser Architecture](#10-parser-architecture)
  - [10.1. Streaming Parse](#101-streaming-parse)
  - [10.2. Flat Attribute Extraction](#102-flat-attribute-extraction)
  - [10.3. Output Modes](#103-output-modes)
  - [10.4. Media Stripping](#104-media-stripping)
  - [10.5. Schema Validation](#105-schema-validation)
- [11. JSON Output Format](#11-json-output-format)
  - [11.1. Separate Mode](#111-separate-mode)
  - [11.2. Combined Mode](#112-combined-mode)
  - [11.3. JSON Schema](#113-json-schema)
- [12. CLI Interface](#12-cli-interface)
  - [12.1. Command Structure](#121-command-structure)
  - [12.2. Global Flags](#122-global-flags)
  - [12.3. parse Subcommand](#123-parse-subcommand)
  - [12.4. report Subcommand](#124-report-subcommand)
  - [12.5. version Subcommand](#125-version-subcommand)
  - [12.6. Exit Codes](#126-exit-codes)
- [13. Report Types](#13-report-types)
  - [13.1. Summary Report](#131-summary-report)
  - [13.2. Contacts Report](#132-contacts-report)
  - [13.3. Timeline Report](#133-timeline-report)
- [14. Repository Layout](#14-repository-layout)
- [15. Documentation Site](#15-documentation-site)
  - [15.1. Site Configuration](#151-site-configuration)
  - [15.2. Navigation Structure](#152-navigation-structure)
  - [15.3. Changelog Synchronization](#153-changelog-synchronization)
  - [15.4. Build and Preview](#154-build-and-preview)
  - [15.5. Deployment](#155-deployment)
  - [15.6. Dependencies](#156-dependencies)

<a name="1-document-information" id="1-document-information"></a>
<hr class="print-page-break">

## 1. Document Information

<a name="11-purpose-and-audience" id="11-purpose-and-audience"></a>
### 1.1. Purpose and Audience

<div style="text-align:justify">

This specification is the authoritative technical reference for the SMS Backup & Restore Parser project. It documents the upstream XML format produced by SyncTech's SMS Backup & Restore Android application, the parser's architecture and behavioral contracts, the CLI interface, the JSON output format, and the project's documentation infrastructure.

</div>

<div style="text-align:justify">

The primary audience is AI coding agents operating in isolated context windows. All sections are self-contained: an agent reading this document has the complete context needed to implement, modify, or extend any component of the project without consulting external sources. The secondary audience is human developers who contribute to or review the project.

</div>

<div style="text-align:justify">

This specification does NOT serve as a user guide, tutorial, or end-user documentation. Those artifacts are maintained separately in the `docs/` directory and published via the documentation site (see [§15](#15-documentation-site)).

</div>

<a name="12-scope" id="12-scope"></a>
### 1.2. Scope

#### In Scope

- **Upstream XML format.** Complete field-level documentation of the SMS, MMS, and call log XML backup format produced by SyncTech's SMS Backup & Restore application. Field semantics, enum values, structural invariants, and known XSD deficiencies.
- **Parser architecture.** Streaming parse strategy, attribute extraction model, output modes, and media stripping behavior.
- **JSON output format.** Schema-validated JSON structure for both separate and combined output modes.
- **CLI interface.** Subcommand structure, flags, exit codes, and verbosity model.
- **Report types.** Summary, contacts, and timeline report specifications.
- **Repository layout.** File and directory structure conventions.
- **Documentation site.** MkDocs configuration, navigation, deployment, and styling conventions.

#### Out of Scope

- **SyncTech application internals.** This specification documents the XML output format, not the application that produces it.
- **Downstream consumers.** Tools that consume the parser's JSON output (DuckDB queries, jq pipelines, custom scripts) are outside the scope of this document.

<a name="13-document-maintenance" id="13-document-maintenance"></a>
### 1.3. Document Maintenance

<div style="text-align:justify">

This specification is maintained as a living document alongside the codebase. It resides at `reference/knowledge-base.md` in the repository. When the specification and the implementation disagree, the specification is presumed correct unless a deliberate amendment has been recorded in the document history.

</div>

<div style="text-align:justify">

When specification text is amended as a result of a sprint batch, each modified section receives an amendment callout in the following format: `> **Updated YYYY-MM-DD:**` followed by a description of the change. Cross-references use §X.Y notation and are verified after all edits to ensure consistency.

</div>

<a name="14-conventions-used-in-this-document" id="14-conventions-used-in-this-document"></a>
### 1.4. Conventions Used in This Document

<div style="text-align:justify">

This specification uses the requirement level keywords defined in RFC 2119. "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" carry their RFC 2119 meanings when capitalized.

</div>

<a name="15-terminology" id="15-terminology"></a>
### 1.5. Terminology

| Term | Definition |
|------|------------|
| Upstream | SyncTech's SMS Backup & Restore application and its official documentation. |
| XSD | The XML Schema Definition published by SyncTech at `sms.xsd_.txt`. |
| Java epoch milliseconds | Milliseconds elapsed since 1970-01-01 00:00:00 UTC, the timestamp format used by Android. |
| Record | A single SMS, MMS, or call log entry in the XML backup. |
| Combined mode | Parser output mode that writes all record types to a single JSON file. |
| Separate mode | Parser output mode (the default) that writes one JSON file per record type. |

<a name="16-reference-documents" id="16-reference-documents"></a>
### 1.6. Reference Documents

| Document | Location | Description |
|----------|----------|-------------|
| Upstream field definitions | [synctech.com.au/.../fields-in-xml-backup-files/](https://www.synctech.com.au/sms-backup-restore/fields-in-xml-backup-files/) | Official documentation of XML attribute names, types, and semantics. |
| Upstream XSD | [synctech.com.au/.../sms.xsd_.txt](https://synctech.com.au/wp-content/uploads/2018/01/sms.xsd_.txt) | XML Schema Definition for the `<smses>` root element. Does not cover `<calls>` or `<addrs>`. |
| JSON Schema | `sms-backup-restore.schema.json` (repository root) | JSON Schema (draft-07) derived from upstream field definitions. This is the project's source of truth for field names, types, and enum semantics. |
| CLAUDE.md | `CLAUDE.md` (repository root) | Claude Code agent instructions covering coding conventions, architecture decisions, and development workflow. |
| Copilot Instructions | `.github/copilot-instructions.md` | GitHub Copilot context mirroring the CLAUDE.md conventions. |

<div style="text-align:justify">

When the upstream documentation and the local JSON Schema conflict, the local schema takes precedence. The schema is updated deliberately when upstream changes warrant it.

</div>

> **Provenance note:** The upstream XML format documentation in §3 through §9 is derived entirely from SyncTech's published XSD, official field reference pages, and the XSL stylesheets distributed with the application. All prose is original and independently composed.

<a name="2-project-overview" id="2-project-overview"></a>
<hr class="print-page-break">

## 2. Project Overview

<a name="21-project-identity" id="21-project-identity"></a>
### 2.1. Project Identity

| Property | Value |
|----------|-------|
| <span style="white-space: nowrap;">Product name</span> | SMS Backup & Restore Parser |
| <span style="white-space: nowrap;">Organization</span> | ShruggieTech LLC (https://shruggie.tech) |
| <span style="white-space: nowrap;">Author</span> | William Thompson |
| <span style="white-space: nowrap;">Language</span> | Python 3.12+ |
| <span style="white-space: nowrap;">Package name</span> | `sms_backup_parser` |
| <span style="white-space: nowrap;">CLI command</span> | `sms-backup-parser` |
| <span style="white-space: nowrap;">License</span> | Apache License 2.0 |

<div style="text-align:justify">

The SMS Backup & Restore Parser is a CLI utility that converts SyncTech SMS Backup & Restore XML exports into structured, schema-validated JSON and generates analytical reports. It is distributed as standalone executables for Windows and Ubuntu, requiring no Python installation on the target system.

</div>

<a name="22-design-goals" id="22-design-goals"></a>
### 2.2. Design Goals

<div style="text-align:justify">

The parser handles multi-gigabyte XML files with constant memory usage. All record types (SMS, MMS, call logs) are supported in a single tool. JSON output conforms to a documented schema and is suitable for downstream analysis with tools such as DuckDB, jq, or custom scripts. Built-in reports provide immediate analytical value without requiring external tooling.

</div>

<a name="23-non-goals" id="23-non-goals"></a>
### 2.3. Non-Goals

<div style="text-align:justify">

The parser does not modify, create, or merge XML backup files. It does not decrypt encrypted (Pro) backups; decryption is a prerequisite step. It does not provide a GUI or web interface. It does not communicate with the SyncTech application or any Android device.

</div>

<a name="24-platform-and-runtime-requirements" id="24-platform-and-runtime-requirements"></a>
### 2.4. Platform and Runtime Requirements

<div style="text-align:justify">

Development requires Python 3.12 or later. The core parse path uses only the Python standard library. Optional dependencies (`jsonschema` for validation, `pyinstaller` for builds) are declared in `pyproject.toml` under named extras. Standalone executables are self-contained and require no Python installation. Windows 10+ and Ubuntu 22.04+ are the supported distribution targets.

</div>

<a name="3-upstream-xml-format" id="3-upstream-xml-format"></a>
<hr class="print-page-break">

## 3. Upstream XML Format

<a name="31-file-structure" id="31-file-structure"></a>
### 3.1. File Structure

<div style="text-align:justify">

SMS Backup & Restore generates two distinct types of XML backup files. Message backups (containing both SMS and MMS records) use a `<smses>` root element. Call log backups use a `<calls>` root element. These are always separate files; messages and calls never appear in the same XML document.

</div>

**Message backup skeleton:**

```xml
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<smses count="N">
  <sms ... />
  <mms ...>
    <parts>
      <part ... />
      <part ... />
    </parts>
    <addrs>
      <addr ... />
      <addr ... />
    </addrs>
  </mms>
  <sms ... />
  <!-- sms and mms elements may be interleaved freely -->
</smses>
```

**Call log backup skeleton:**

```xml
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<calls count="N">
  <call ... />
  <call ... />
</calls>
```

<a name="32-structural-invariants" id="32-structural-invariants"></a>
### 3.2. Structural Invariants

<div style="text-align:justify">

The `count` attribute on the root element reports the total number of child records in the file. Within `<smses>`, `<sms>` and `<mms>` elements appear in any order, interleaved chronologically rather than grouped by type. Each `<mms>` element contains a `<parts>` wrapper (with one or more `<part>` children) and MAY contain an `<addrs>` wrapper (with one or more `<addr>` children). The `<addrs>` element is present in real-world exports but is not defined in the official XSD schema.

</div>

<div style="text-align:justify">

File sizes for long-term users routinely reach hundreds of megabytes to multiple gigabytes, primarily driven by base64-encoded MMS media. The XML declaration specifies `encoding='UTF-8'`. When the app preference "Add XSL Tag" is enabled, the XML includes an `<?xml-stylesheet?>` processing instruction referencing `sms.xsl` or `calls.xsl`, allowing browser-based rendering. When "Add Readable Date" is enabled, `readable_date` and `contact_name` optional attributes are populated on each record.

</div>

<a name="4-sms-fields" id="4-sms-fields"></a>
<hr class="print-page-break">

## 4. SMS Fields

<div style="text-align:justify">

Each `<sms>` element is a self-closing tag whose entire payload is carried in XML attributes. There are no child elements.

</div>

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `protocol` | `xs:unsignedByte` | No | Transport protocol identifier. Almost always `0` for standard SMS. | Typically `0` |
| `address` | `xs:string` | Yes | Phone number of the sender or recipient. Format varies by carrier and locale (may include country code, spaces, dashes, or leading `+`). | Phone number string |
| `date` | `xs:unsignedLong` | Yes | Timestamp in Java epoch milliseconds. See [§8](#8-date-handling). | Millisecond epoch integer |
| `type` | `xs:unsignedByte` | Yes | Message direction/disposition. See [§7.1](#71-sms-type). | `1`–`6` |
| `subject` | `xs:string` | No | Message subject line. Rarely used for SMS; more common in MMS. | Any string or `"null"` |
| `body` | `xs:string` | Yes | Message text content. | Any string |
| `toa` | `xs:string` | No | Type of Address. BCD encoding indicator for the address field. | Typically `"null"` |
| `sc_toa` | `xs:string` | No | Service Center Type of Address. BCD encoding indicator for the SMSC number. | Typically `"null"` |
| `service_center` | `xs:string` | No | SMSC (Short Message Service Center) number that routed the message. | Phone number string or `"null"` |
| `read` | `xs:unsignedByte` | Yes | Read status. See [§7.3](#73-smsmms-read). | `0` or `1` |
| `status` | `xs:byte` | Yes | Delivery status. See [§7.2](#72-sms-status). | `-1`, `0`, `32`, `64` |
| `locked` | `xs:unsignedByte` | No | Whether the message is locked (protected from deletion). | `0` = unlocked, `1` = locked |
| `date_sent` | `xs:unsignedLong` | No | Sender-side timestamp in Java epoch milliseconds. See [§8.3](#83-date-vs-date_sent). | Millisecond epoch integer or `0` |
| `sub_id` | `xs:string` | No | SIM subscription ID. Identifies which SIM handled the message on dual-SIM devices. | Index integer or full SIM ID string |
| `readable_date` | `xs:string` | No | Human-friendly date rendering. Present only when enabled in backup preferences. | Formatted date string |
| `contact_name` | `xs:string` | No | Contact display name matched to the `address` field. Present only when enabled. | Any string |

<a name="5-mms-fields" id="5-mms-fields"></a>
<hr class="print-page-break">

## 5. MMS Fields

<a name="51-mms-record-attributes" id="51-mms-record-attributes"></a>
### 5.1. MMS Record Attributes

<div style="text-align:justify">

Each `<mms>` element carries its metadata as XML attributes. Additionally, it contains nested `<parts>` and (optionally) `<addrs>` child elements. The MMS attribute set is substantially larger than SMS, reflecting the complexity of the MMS protocol (OMA MMS Encapsulation).

</div>

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `date` | `xs:unsignedLong` | Yes | Timestamp in Java epoch milliseconds. | Millisecond epoch integer |
| `ct_t` | `xs:string` | Yes | Content-Type of the MMS message. | Typically `"application/vnd.wap.multipart.related"` |
| `msg_box` | `xs:unsignedByte` | Yes | Message box (folder). See [§7.4](#74-mms-message-box). | `1`–`4` |
| `rr` | `xs:unsignedByte` | Yes | Read report request. `128` = requested, `129` = not requested. | `128` or `129` |
| `read_status` | `xs:unsignedByte` | No | Read report status from the recipient side. | Integer |
| `address` | `xs:string` | Yes | Primary address (sender or recipient). On MMS, the XSD types this as `xs:long`, but real-world values contain phone number strings. | Phone number string |
| `m_id` | `xs:string` | Yes | Message ID assigned by the MMS gateway. Globally unique identifier for the MMS transaction. | URI-style string |
| `read` | `xs:unsignedByte` | Yes | Local read status. See [§7.3](#73-smsmms-read). | `0` or `1` |
| `m_size` | `xs:string` | No | Message size in bytes as reported by the gateway. | Integer string |
| `m_type` | `xs:unsignedByte` | Yes | MMS message type (PDU type). `128` = send request, `132` = retrieve confirmation. | Integer |
| `retr_st` | `xs:unsignedByte` | No | Retrieve status code. `0` usually indicates success. | Integer |
| `ct_cls` | `xs:unsignedByte` | No | Content class. | Integer |
| `sub_cs` | `xs:string` | No | Subject character set (IANA number). | Integer string |
| `ct_l` | `xs:string` | No | Content-Location. URL from which the MMS content was retrieved. | URL string |
| `tr_id` | `xs:string` | Yes | Transaction ID for the MMS exchange. | String |
| `st` | `xs:unsignedByte` | No | Delivery status. | Integer |
| `m_cls` | `xs:string` | No | Message class (e.g., `"personal"`, `"advertisement"`). | String |
| `d_tm` | `xs:string` | No | Delivery time. | Epoch string |
| `retr_txt_cs` | `xs:unsignedByte` | No | Retrieve text character set. | Integer |
| `d_rpt` | `xs:unsignedByte` | No | Delivery report requested. `128` = requested. | `128` or `129` |
| `date_sent` | `xs:unsignedLong` | No | Sender-side timestamp. See [§8.3](#83-date-vs-date_sent). | Millisecond epoch integer or `0` |
| `seen` | `xs:unsignedByte` | No | Whether the notification was seen. | `0` or `1` |
| `v` | `xs:unsignedByte` | No | MMS version. | Integer |
| `exp` | `xs:string` | No | Message expiry time. | Epoch string |
| `pri` | `xs:unsignedByte` | No | Priority. `128` = low, `129` = normal, `130` = high. | `128`, `129`, or `130` |
| `resp_txt` | `xs:string` | No | Response text from the gateway. | String |
| `rpt_a` | `xs:unsignedByte` | No | Report allowed flag. | Integer |
| `locked` | `xs:unsignedByte` | No | Locked status. | `0` or `1` |
| `retr_txt` | `xs:string` | No | Retrieve text. | String |
| `resp_st` | `xs:unsignedByte` | No | Response status from the gateway. | Integer |
| `text_only` | `xs:unsignedByte` | No | Whether the MMS contains only text parts (no media). | `0` or `1` |
| `sub` | `xs:string` | No | Message subject. | Any string |
| `sub_id` | `xs:string` | No | SIM subscription ID. | Index integer or full SIM ID string |
| `readable_date` | `xs:string` | No | Human-friendly date rendering. Present only when enabled. | Formatted date string |
| `contact_name` | `xs:string` | No | Contact display name. Present only when enabled. | Any string |

<a name="52-mms-part-fields" id="52-mms-part-fields"></a>
### 5.2. MMS Part Fields

<div style="text-align:justify">

Each `<part>` element inside `<parts>` represents one component of the MMS message. A typical MMS contains at least a SMIL layout part and one content part (text or media).

</div>

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `seq` | `xs:byte` | Yes | Sequence number controlling the display order of parts. | Integer (starting from `-1` or `0`) |
| `ct` | `xs:string` | Yes | MIME content type of this part. | MIME type string (e.g., `"text/plain"`, `"image/jpeg"`) |
| `name` | `xs:string` | Yes | Part name, often derived from the original filename. | String or `"null"` |
| `chset` | `xs:string` | Yes | Character set as an IANA number (e.g., `"106"` for UTF-8). | Integer string or `"null"` |
| `cd` | `xs:string` | Yes | Content-Disposition header value. | String or `"null"` |
| `fn` | `xs:string` | Yes | Filename from content headers. | String or `"null"` |
| `cid` | `xs:string` | Yes | Content-ID for referencing this part from SMIL layout. | String or `"null"` |
| `cl` | `xs:string` | Yes | Content-Location identifier. | String or `"null"` |
| `ctt_s` | `xs:string` | Yes | Content-Type start parameter. Identifies the root part of the multipart message. | String or `"null"` |
| `ctt_t` | `xs:string` | Yes | Content-Type type parameter. Specifies the overall type of the multipart message. | String or `"null"` |
| `text` | `xs:string` | Yes | Text content of the part. Populated for `text/plain` parts; typically `"null"` for binary parts. | Message text or `"null"` |
| `data` | `xs:string` | No | Base64-encoded binary payload. Present for media parts (images, audio, video). This field is the primary driver of large file sizes in MMS backups. | Base64 string |

<a name="53-common-mms-content-types" id="53-common-mms-content-types"></a>
### 5.3. Common MMS Content Types

| MIME Type | Description |
|-----------|-------------|
| `application/smil` | SMIL (Synchronized Multimedia Integration Language) layout descriptor controlling how MMS parts are presented. Nearly every MMS contains one. |
| `text/plain` | Plain text body of the message. The actual text is in the `text` attribute. |
| `image/jpeg` | JPEG photograph or image. Binary data in the `data` attribute. |
| `image/png` | PNG image. Binary data in the `data` attribute. |
| `image/gif` | GIF image (may be animated). Binary data in the `data` attribute. |
| `audio/mpeg` | MP3 or other MPEG audio. Binary data in the `data` attribute. |
| `audio/amr` | AMR audio recording, common for voice notes. |
| `video/mp4` | MP4 video. Binary data in the `data` attribute. |
| `video/3gpp` | 3GPP video, commonly recorded on older Android devices. |

<a name="54-mms-address-fields" id="54-mms-address-fields"></a>
### 5.4. MMS Address Fields

<div style="text-align:justify">

Each `<addr>` element inside `<addrs>` identifies one participant in the MMS conversation. Group MMS messages have multiple `<addr>` entries, one for each recipient and one for the sender.

</div>

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `address` | string | Yes | Phone number or email address of this participant. | Phone number or address string |
| `type` | integer | Yes | Role of this participant in the message. Values correspond to the PduHeaders constants in the Android telephony stack. | `129` = BCC, `130` = CC, `137` = From, `151` = To |
| `charset` | integer | Yes | Character set identifier for this address entry. | Integer (e.g., `106` for UTF-8) |

<div style="text-align:justify">

The `<addrs>` wrapper and its `<addr>` children are present in real-world backup exports but are not defined in the official XSD schema published by SyncTech. Parsers MUST expect them to be present but MUST NOT fail if they are absent.

</div>

<a name="6-call-log-fields" id="6-call-log-fields"></a>
<hr class="print-page-break">

## 6. Call Log Fields

<div style="text-align:justify">

Each `<call>` element represents one entry in the phone's call history. Like SMS, all data is carried in XML attributes with no child elements.

</div>

| Field | XSD Type | Required | Description | Valid Values |
|-------|----------|----------|-------------|--------------|
| `number` | string | Yes | Phone number associated with the call. May include country code prefixes. | Phone number string |
| `duration` | integer | Yes | Length of the call in seconds. `0` for missed or rejected calls. | Non-negative integer |
| `date` | `xs:unsignedLong` | Yes | Timestamp in Java epoch milliseconds. See [§8](#8-date-handling). | Millisecond epoch integer |
| `type` | integer | Yes | Call direction/disposition. See [§7.6](#76-call-type). | `1`–`6` |
| `presentation` | integer | Yes | Caller ID presentation status. See [§7.7](#77-call-presentation). | `1`–`4` |
| `subscription_id` | string | No | SIM subscription that handled the call. On dual-SIM devices, this distinguishes which line was used. | Index integer or full SIM ID string |
| `readable_date` | string | No | Human-friendly date rendering. Present only when enabled in backup preferences. | Formatted date string |
| `contact_name` | string | No | Contact display name matched to the `number` field. Present only when enabled. | Any string |

> **Note:** Call logs use a separate `<calls>` root element and are stored in their own XML file. The official XSD only covers the `<smses>` root element. The `<calls>` structure is confirmed by the `calls.xsl` stylesheet distributed by SyncTech and by real-world backup files.

<a name="7-enum-reference" id="7-enum-reference"></a>
<hr class="print-page-break">

## 7. Enum Reference

<a name="71-sms-type" id="71-sms-type"></a>
### 7.1. SMS Type

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |
| `5` | Failed |
| `6` | Queued |

<a name="72-sms-status" id="72-sms-status"></a>
### 7.2. SMS Status

| Value | Meaning |
|-------|---------|
| `-1` | None (no delivery status available) |
| `0` | Complete (delivered successfully) |
| `32` | Pending (delivery in progress) |
| `64` | Failed (delivery failed) |

<a name="73-smsmms-read" id="73-smsmms-read"></a>
### 7.3. SMS/MMS Read

| Value | Meaning |
|-------|---------|
| `0` | Unread |
| `1` | Read |

<a name="74-mms-message-box" id="74-mms-message-box"></a>
### 7.4. MMS Message Box

| Value | Meaning |
|-------|---------|
| `1` | Received |
| `2` | Sent |
| `3` | Draft |
| `4` | Outbox |

<a name="75-mms-address-type" id="75-mms-address-type"></a>
### 7.5. MMS Address Type

| Value | Meaning |
|-------|---------|
| `129` | BCC |
| `130` | CC |
| `137` | From |
| `151` | To |

<a name="76-call-type" id="76-call-type"></a>
### 7.6. Call Type

| Value | Meaning |
|-------|---------|
| `1` | Incoming |
| `2` | Outgoing |
| `3` | Missed |
| `4` | Voicemail |
| `5` | Rejected |
| `6` | Refused List |

<a name="77-call-presentation" id="77-call-presentation"></a>
### 7.7. Call Presentation

| Value | Meaning |
|-------|---------|
| `1` | Allowed (caller ID visible) |
| `2` | Restricted (caller ID withheld) |
| `3` | Unknown |
| `4` | Payphone |

<a name="8-date-handling" id="8-date-handling"></a>
<hr class="print-page-break">

## 8. Date Handling

<a name="81-epoch-format" id="81-epoch-format"></a>
### 8.1. Epoch Format

<div style="text-align:justify">

All timestamp fields (`date`, `date_sent`) use Java epoch milliseconds: the number of milliseconds elapsed since 1970-01-01 00:00:00 UTC.

</div>

<a name="82-conversion" id="82-conversion"></a>
### 8.2. Conversion

To obtain a standard Unix timestamp (seconds), divide by 1000:

```
unix_seconds = date_ms / 1000
```

To convert to an ISO 8601 string in Python:

```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(date_ms / 1000, tz=timezone.utc)
iso_str = dt.isoformat()
```

In Excel, the formula `=(date_ms / 86400000) + 25569` converts to an Excel date serial number (format the cell as date/time afterward).

<a name="83-date-vs-date_sent" id="83-date-vs-date_sent"></a>
### 8.3. date vs date_sent

<div style="text-align:justify">

These are distinct fields serving different purposes. `date` is the timestamp recorded by the local device. For received messages, this is when the message arrived. For sent messages, this is typically when the message was dispatched. `date_sent` is the timestamp from the originating device or network. For received messages, this reflects when the sender actually sent it. The value MAY be `0` or absent if the network did not provide the information.

</div>

<a name="84-readable_date" id="84-readable_date"></a>
### 8.4. readable_date

<div style="text-align:justify">

This optional field contains a locale-formatted date string generated at backup time. The format is controlled by the app's "Readable Date Format" setting and varies between users. Parsers SHOULD NOT rely on this field for programmatic date operations; use the `date` epoch value instead.

</div>

<a name="85-computed-date_iso-field" id="85-computed-date_iso-field"></a>
### 8.5. Computed date_iso Field

<div style="text-align:justify">

The parser injects a computed `date_iso` field (ISO 8601, UTC) derived from the `date` attribute on every record. This is a convenience field for human readability and tooling interoperability. It is not present in the upstream XML. Injection is enabled by default and can be suppressed with the `--no-date-iso` CLI flag (see [§12.3](#123-parse-subcommand)).

</div>

<a name="9-xsd-known-issues" id="9-xsd-known-issues"></a>
<hr class="print-page-break">

## 9. XSD Known Issues

<a name="91-missing-definitions" id="91-missing-definitions"></a>
### 9.1. Missing Definitions

<div style="text-align:justify">

The official XSD does not define the `<addrs>` wrapper element or its `<addr>` children within `<mms>`. Despite this omission, the `<addrs>` structure is consistently present in real backup files. The addr type enum values (`129`, `130`, `137`, `151`) are documented in the official field reference and MUST be supported.

</div>

<div style="text-align:justify">

The XSD only describes the `<smses>` root element. Call log backups use a `<calls>` root element that is not covered by the XSD but is confirmed by the `calls.xsl` stylesheet and by real-world files.

</div>

<a name="92-type-mismatches" id="92-type-mismatches"></a>
### 9.2. Type Mismatches

Several XSD type declarations are incorrect or overly restrictive compared to real-world data:

| Field | XSD Type | Actual Behavior |
|-------|----------|-----------------|
| MMS `address` | `xs:long` | Contains phone number strings (including `+` prefixes and non-numeric characters). |
| MMS `date_sent` | `xs:unsignedByte` | Holds epoch millisecond values (large integers). |
| Root `count` | `xs:unsignedShort` (max 65,535) | Backup files routinely contain far more records. |

<div style="text-align:justify">

Parsers MUST treat all attribute values as strings and perform type conversion explicitly rather than relying on the XSD type declarations.

</div>

<a name="93-rcs-and-advanced-messages" id="93-rcs-and-advanced-messages"></a>
### 9.3. RCS and Advanced Messages

<div style="text-align:justify">

Newer versions of the app (v10.15.002+) support backing up RCS (Rich Communication Services) messages on selected devices, specifically those using Samsung Messages. These are stored within the same XML structure but MAY include additional attributes or edge cases not covered by the original schema.

</div>

<a name="94-backup-encryption" id="94-backup-encryption"></a>
### 9.4. Backup Encryption

<div style="text-align:justify">

The Pro version of the app (v10.05.301+) can compress and encrypt backups using ZIP with AES-256 encryption. Encrypted backup files MUST be decrypted before XML parsing. The underlying XML format remains the same after decryption.

</div>

<a name="10-parser-architecture" id="10-parser-architecture"></a>
<hr class="print-page-break">

## 10. Parser Architecture

<a name="101-streaming-parse" id="101-streaming-parse"></a>
### 10.1. Streaming Parse

<div style="text-align:justify">

The parser uses `xml.etree.ElementTree.iterparse` with explicit `elem.clear()` calls to avoid loading the full DOM into memory. This is a hard architectural constraint: XML exports routinely reach multiple gigabytes. Refactoring to `ET.parse()` or other full-tree approaches is prohibited.

</div>

<a name="102-flat-attribute-extraction" id="102-flat-attribute-extraction"></a>
### 10.2. Flat Attribute Extraction

<div style="text-align:justify">

SMS and call records map 1:1 from XML attributes to JSON object keys via `dict(elem.attrib)`. MMS records additionally collect nested `<part>` and `<addr>` child elements into `parts` and `addrs` arrays. This flat extraction pattern is intentional. ORM-style classes or dataclass wrappers are not used unless the project explicitly moves to that model.

</div>

<a name="103-output-modes" id="103-output-modes"></a>
### 10.3. Output Modes

<div style="text-align:justify">

The parser supports two output modes. In separate mode (the default), the parser writes one JSON file per record type found in the input: `<stem>_sms.json`, `<stem>_mms.json`, and `<stem>_calls.json`. In combined mode (`--combined`), a single `<stem>.json` file is written containing top-level `sms`, `mms`, and `calls` arrays. Combined mode uses temporary per-section files that are assembled into the final output to handle interleaved record types without buffering the entire dataset in memory.

</div>

<a name="104-media-stripping" id="104-media-stripping"></a>
### 10.4. Media Stripping

<div style="text-align:justify">

The `--strip-media` flag omits the `data` attribute from MMS `<part>` elements during extraction. This significantly reduces output file size for analytical use cases where the base64-encoded media content is not needed.

</div>

<a name="105-schema-validation" id="105-schema-validation"></a>
### 10.5. Schema Validation

<div style="text-align:justify">

The `--validate` flag triggers a post-write validation pass against the project's JSON Schema (`sms-backup-restore.schema.json`). This requires the `jsonschema` package, which is declared as an optional dependency under the `[validate]` extra. Validation errors cause a non-zero exit code (see [§12.6](#126-exit-codes)).

</div>

<a name="11-json-output-format" id="11-json-output-format"></a>
<hr class="print-page-break">

## 11. JSON Output Format

<a name="111-separate-mode" id="111-separate-mode"></a>
### 11.1. Separate Mode

<div style="text-align:justify">

Each per-type file contains a top-level JSON array of record objects. The file naming convention is `<input_stem>_<type>.json`, where `<type>` is one of `sms`, `mms`, or `calls`. Files are only written for record types that are present in the input.

</div>

<a name="112-combined-mode" id="112-combined-mode"></a>
### 11.2. Combined Mode

The combined output file is a JSON object with three keys:

```json
{
  "sms": [ ... ],
  "mms": [ ... ],
  "calls": [ ... ]
}
```

Empty arrays are included for record types not present in the input.

<a name="113-json-schema" id="113-json-schema"></a>
### 11.3. JSON Schema

<div style="text-align:justify">

The file `sms-backup-restore.schema.json` at the repository root is a JSON Schema (draft-07) document that defines the expected structure of the parser's output. It covers all SMS, MMS (including parts and addrs), and call record fields with descriptions, types, enum constraints, and required-field declarations. The schema is the project's source of truth for field semantics. When the schema and the upstream documentation conflict, the schema takes precedence.

</div>

<a name="12-cli-interface" id="12-cli-interface"></a>
<hr class="print-page-break">

## 12. CLI Interface

<a name="121-command-structure" id="121-command-structure"></a>
### 12.1. Command Structure

<div style="text-align:justify">

The CLI uses `argparse` with full subcommand support. The top-level command is `sms-backup-parser`. Three subcommands are available: `parse`, `report`, and `version`.

</div>

<a name="122-global-flags" id="122-global-flags"></a>
### 12.2. Global Flags

| Flag | Description |
|------|-------------|
| `-v` / `--verbose` | Increase output verbosity. Shows per-record detail, file paths, and extended timing. |
| `-q` / `--quiet` | Suppress all non-error output. Only fatal errors are printed to stderr. |

These flags are mutually exclusive and MUST appear before the subcommand name.

<a name="123-parse-subcommand" id="123-parse-subcommand"></a>
### 12.3. parse Subcommand

```
sms-backup-parser parse [options] <input> [<input> ...]
```

| Flag | Default | Description |
|------|---------|-------------|
| `-o` / `--output-dir DIR` | Same directory as input | Directory for output JSON files (created if missing). |
| `--combined` | Off | Write a single combined JSON file instead of per-type files. |
| `--strip-media` | Off | Omit base64-encoded media data from MMS parts. |
| `--no-date-iso` | Off | Skip injection of computed `date_iso` fields. |
| `--validate` | Off | Validate output against the JSON Schema after writing. Requires `[validate]` extra. |
| `--pretty` | On | Pretty-print JSON with 2-space indentation. |
| `--compact` | Off | Write compact JSON with no whitespace. Mutually exclusive with `--pretty`. |

<a name="124-report-subcommand" id="124-report-subcommand"></a>
### 12.4. report Subcommand

```
sms-backup-parser report [options] <input> [<input> ...]
```

| Flag | Default | Description |
|------|---------|-------------|
| `-t` / `--type TYPE` | `summary` | Report type: `summary`, `contacts`, `timeline`, or `all`. |
| `-o` / `--output FILE` | stdout | File path to write the report. |
| `--format FORMAT` | `text` | Output format: `text`, `csv`, or `json`. |
| `--top-n N` | `20` | Number of entries in ranked reports. |

<a name="125-version-subcommand" id="125-version-subcommand"></a>
### 12.5. version Subcommand

```
sms-backup-parser version
```

Prints the installed version number and exits.

<a name="126-exit-codes" id="126-exit-codes"></a>
### 12.6. Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success. |
| `1` | User error (bad arguments, missing files, missing dependencies). |
| `2` | Parse or data error (malformed XML, validation failure). |

<a name="13-report-types" id="13-report-types"></a>
<hr class="print-page-break">

## 13. Report Types

<a name="131-summary-report" id="131-summary-report"></a>
### 13.1. Summary Report

<div style="text-align:justify">

The summary report provides aggregate statistics across all records in the input files. It includes total counts by record type (SMS, MMS, calls), date range (earliest and latest record), breakdown by direction (sent/received for messages, incoming/outgoing/missed for calls), message read/unread counts, MMS media vs. text-only counts, unique contact count, and total call duration.

</div>

<a name="132-contacts-report" id="132-contacts-report"></a>
### 13.2. Contacts Report

<div style="text-align:justify">

The contacts report ranks contacts by message and call volume. The number of entries is controlled by `--top-n` (default: 20). For each contact, it reports the phone number, contact name (if available), SMS received/sent counts, MMS received/sent counts, call counts by direction, total call duration, and first/last activity dates.

</div>

<a name="133-timeline-report" id="133-timeline-report"></a>
### 13.3. Timeline Report

<div style="text-align:justify">

The timeline report aggregates message and call activity by date. Each row reports the date, SMS count, MMS count, call count, and total call duration for that period.

</div>

<a name="14-repository-layout" id="14-repository-layout"></a>
<hr class="print-page-break">

## 14. Repository Layout

```
.
├── CLAUDE.md                          # Claude Code agent instructions
├── LICENSE                            # Apache License 2.0
├── CHANGELOG.md                       # Keep a Changelog format
├── README.md                          # Project overview and quick start
├── .gitignore                         # VCS exclusions
├── pyproject.toml                     # PEP 621 metadata, build config, tool settings
├── mkdocs.yml                         # MkDocs documentation site config
├── sms-backup-restore.schema.json     # JSON Schema (draft-07) — source of truth
├── src/
│   └── sms_backup_parser/             # Main package
│       ├── __init__.py                # Package version
│       ├── __main__.py                # python -m support
│       ├── cli.py                     # argparse CLI entry point
│       ├── parser.py                  # Streaming XML → JSON transformer
│       ├── reports.py                 # Summary, contacts, and timeline reports
│       ├── models.py                  # Enum constants and lookup tables
│       ├── utils.py                   # Shared helpers (date conversion, formatting)
│       ├── progress.py                # Progress reporting for long parses
│       └── validate.py                # Optional JSON Schema validation
├── tests/                             # pytest test suite
│   ├── fixtures/                      # Synthetic XML test data
│   ├── test_parser.py
│   ├── test_cli.py
│   ├── test_reports.py
│   ├── test_utils.py
│   └── test_models.py
├── scripts/
│   └── build.py                       # PyInstaller build script
├── docs/                              # MkDocs documentation site (see §15)
└── reference/
    └── knowledge-base.md              # This document
```

<a name="15-documentation-site" id="15-documentation-site"></a>
<hr class="print-page-break">

## 15. Documentation Site

<div style="text-align:justify">

The project documentation is published as a static site built with [MkDocs](https://www.mkdocs.org/) using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. This matches the toolchain established by shruggie-indexer and adopted across all ShruggieTech projects.

</div>

<a name="151-site-configuration" id="151-site-configuration"></a>
### 15.1. Site Configuration

The site is configured by `mkdocs.yml` at the repository root.

| Setting | Value | Purpose |
|---------|-------|---------|
| <span style="white-space: nowrap;">`site_name`</span> | `SMS Backup & Restore Parser` | Displayed in the site header and browser title. |
| <span style="white-space: nowrap;">`site_description`</span> | Project tagline for SEO and social metadata. | |
| <span style="white-space: nowrap;">`site_url`</span> | The GitHub Pages URL for the project. | Base URL for canonical links and sitemap generation. |
| <span style="white-space: nowrap;">`repo_url`</span> | `https://github.com/ShruggieTech/sms-backup-restore-parser` | Links to the source repository from the site header. |
| <span style="white-space: nowrap;">`docs_dir`</span> | `docs` | MkDocs reads all documentation source from the `docs/` directory. |
| <span style="white-space: nowrap;">`theme.name`</span> | `material` | Activates the Material for MkDocs theme. |
| <span style="white-space: nowrap;">`theme.palette.scheme`</span> | `slate` | Dark mode enabled by default. |
| <span style="white-space: nowrap;">`theme.features`</span> | Navigation tabs, instant loading, search highlighting, content tabs. | Provides a polished, responsive documentation experience. |

Required Markdown extensions: `admonition`, `pymdownx.details`, `pymdownx.superfences`.

<div style="text-align:justify">

The `nav` key in `mkdocs.yml` defines the sidebar navigation structure explicitly rather than relying on directory auto-discovery. This ensures predictable ordering and human-readable section labels.

</div>

<a name="152-navigation-structure" id="152-navigation-structure"></a>
### 15.2. Navigation Structure

```yaml
nav:
  - Home: index.md
  - Installation: installation.md
  - Usage: usage.md
  - Schema Reference: schema.md
  - XML Format Reference: xml-reference.md
  - Reports: reports.md
  - Changelog: changelog.md
```

<div style="text-align:justify">

The XML Format Reference page presents the upstream format documentation from §3 through §9 of this specification in a form suitable for end-user consumption. It serves as a standalone reference for anyone working with the raw XML backup files, independent of this parser.

</div>

<a name="153-changelog-synchronization" id="153-changelog-synchronization"></a>
### 15.3. Changelog Synchronization

<div style="text-align:justify">

The documentation site's changelog page (`docs/changelog.md`) is a copy of `CHANGELOG.md` at the repository root. The copy is maintained manually. The file begins with a header comment identifying it as auto-copied:

</div>

```markdown
<!-- THIS FILE IS AUTO-COPIED FROM CHANGELOG.md AT THE REPOSITORY ROOT. -->
<!-- DO NOT EDIT THIS FILE DIRECTLY. Edit CHANGELOG.md instead. -->
```

<div style="text-align:justify">

The canonical changelog is `CHANGELOG.md` at the repository root. All edits are made there. When the documentation site is built or deployed, `docs/changelog.md` MUST reflect the current state of `CHANGELOG.md`. If the two files diverge, the root `CHANGELOG.md` is authoritative.

</div>

<a name="154-build-and-preview" id="154-build-and-preview"></a>
### 15.4. Build and Preview

| Command | Purpose |
|---------|---------|
| <span style="white-space: nowrap;">`mkdocs serve`</span> | Starts a local development server with live reload at `http://127.0.0.1:8000/`. |
| <span style="white-space: nowrap;">`mkdocs build`</span> | Produces the static site in the `site/` directory. The `site/` directory is listed in `.gitignore` and is never committed. |

<a name="155-deployment" id="155-deployment"></a>
### 15.5. Deployment

<div style="text-align:justify">

The documentation site is deployed to GitHub Pages. The deployment mechanism (manual `mkdocs gh-deploy` or a GitHub Actions workflow) is configured at the repository level. When a CI workflow is used, it SHOULD trigger on push to `main` when files in `docs/` or `mkdocs.yml` change, build the site using `mkdocs build --strict`, and deploy the built `site/` directory to the `gh-pages` branch. The `--strict` flag ensures that broken internal links, missing navigation targets, and unreferenced pages cause build failures.

</div>

<a name="156-dependencies" id="156-dependencies"></a>
### 15.6. Dependencies

<div style="text-align:justify">

`mkdocs` and `mkdocs-material` are declared as optional development dependencies in `pyproject.toml` under a `[project.optional-dependencies]` docs group:

</div>

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.5",
]
```

<div style="text-align:justify">

These packages are not required for using, developing, or testing the parser. They are required only for building or previewing the documentation site. Documentation authors install them with `pip install -e ".[docs]"`.

</div>
