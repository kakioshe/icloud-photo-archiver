# iCloud Photo Archiver

An early-stage project intended to archive a selected date range from iCloud Photos to a local computer. The planned application is not yet available: there is no sign-in, download, user interface, or runnable archive workflow.

The current code is an experimental, offline inspection of synthetic photo-library pages. It identifies repeated asset records and missing master records, and reports interrupted or ambiguous scans as incomplete. It does not connect to iCloud or establish that an entire library can be enumerated. Real account compatibility, security, and download integrity have not been verified.

## Run the tests

With Python 3.11 or newer and Git installed, run from the repository root:

```sh
python -m unittest discover -s tests -v
```

The tests use synthetic records and do not require an Apple account or network access. They are not an account-backed integration test.

## Provider research

The candidate provider is [iCloud Photos Downloader](https://github.com/icloud-photos-downloader/icloud_photos_downloader), specifically its bundled photo service. It has not been installed or integrated. In its [version 1.33.0 implementation](https://github.com/icloud-photos-downloader/icloud_photos_downloader/blob/v1.33.0/src/pyicloud_ipd/services/photos.py), the ordinary collection excludes hidden and deleted assets and the iterator may skip an asset whose master record is unavailable. Coverage and completeness need further investigation before using it for archival.
