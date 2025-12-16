# Test DONE Filtering

This document tests the DONE filtering functionality.

## Regular Links (should be included)
- [Python](https://www.python.org/)
- [GitHub](https://github.com)

## DONE Links (should be filtered out)
- [Completed Task](https://example.com/DONE)
- [Finished Document](https://docs.example.com/DONE)
- [Final Link](https://final.example.org/task/DONE)

## Mixed Links
- [Regular Site](https://example.com)
- [Done Status](https://status.example.com/DONE)
- [Another Regular](<https://openai.com>)

## Reference Style with DONE
This is a [regular link][regular-ref] and a [DONE link][done-ref].

[regular-ref]: https://documentation.example.org
[done-ref]: https://finished.example.com/DONE
