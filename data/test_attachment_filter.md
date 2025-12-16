# Test Attachment Filtering

This document tests the @attachment filtering functionality.

## Regular Links (should be included)
- [Python](https://www.python.org/)
- [GitHub](https://github.com)

## Attachment Links (should be filtered out)
- [Document](https://example.com@attachment)
- [Image](./images/photo.png@attachment)
- [File](ftp://files.com/document.pdf@attachment)

## Mixed Links
- [Regular Site](https://example.com)
- [Attachment Link](mailto:user@company.com@attachment)
- [Another Regular](<https://openai.com>)

## Reference Style with Attachments
This is a [reference link][attachment-ref] and a [regular link][regular-ref].

[attachment-ref]: https://site.com@attachment
[regular-ref]: https://documentation.example.org

## Auto-links with Attachments
Check <https://docs.python.org@attachment> and <https://stackoverflow.com> for help.
