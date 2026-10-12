# HP LaserJet 1020 driver for macOS / Apple silicon

A small native arm64 USB print driver and installer for the HP LaserJet 1020.
**Successfully printed on macOS 27.0.1 with a real HP LaserJet 1020 on 12 October 2026.**

The Mac renders PDFs with its built-in `cgpdftoraster` filter. This driver converts
the raster to the printer's ZjStream format with JBIG compression. It needs no
Ghostscript, Homebrew libraries or Rosetta at runtime.

## Install

1. Connect the HP LaserJet 1020 by USB and switch it on.
2. Download **HP-LaserJet-1020-Apple-Silicon.pkg** from the
   [latest release](https://github.com/OneCoinOnePlay/hp-laserjet-1020-macos/releases/latest).
3. Open the installer and enter your Mac administrator password when requested.
4. Choose **HP LaserJet 1020** in any app's print dialog.

The installer adds the connected 1020 automatically and preserves an existing
default printer. The package is unsigned and is not notarized by Apple.

If the printer was disconnected during installation, connect it and run:

```sh
sudo /Library/Printers/HP1020/setup-printer.sh
```

The queue is named `HP_LaserJet_1020`. To print a PDF from Terminal:

```sh
lp -d HP_LaserJet_1020 /path/to/document.pdf
```

## What has been tested

- Apple silicon, macOS **27.0.1**, USB, HP LaserJet **1020**.
- A real single-page PDF printed successfully and the queue returned to idle.
- Native arm64 executable, valid PPD, A4 defaults, **600 × 600 dpi** monochrome.
- The build check renders a PDF and validates the firmware prefix and complete
  ZjStream page structure without sending anything to a printer.

The driver prepends the printer's volatile firmware before every job and pauses
for two seconds before emitting the page. This is intended to handle printer
power cycles; printing immediately after a power cycle has not been separately
tested. Multi-page jobs, multiple copies, other paper sizes, other macOS releases
and other printer models have not been hardware-tested. There is no scanner or
toner-level support.

## Build from source

Requires an Apple silicon Mac, Python 3 and Xcode Command Line Tools:

```sh
python3 build.py
```

The installer and SHA-256 checksum are written to `dist/`. Build products and the
validation PDF stay under `build/`. Building does not install or print anything.

If your command-line tools are older than your default SDK and the linker reports
an unknown architecture such as `arm64e.x1`, choose an installed compatible SDK:

```sh
python3 build.py --sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.2.sdk
```

## Installed files

The driver, firmware and setup helper live under `/Library/Printers/HP1020`, where
macOS's CUPS sandbox can read them. The PPD lives at
`/Library/Printers/PPDs/Contents/Resources/HP-LaserJet-1020-Apple-Silicon.ppd`.
The installer creates or updates only the `HP_LaserJet_1020` queue.

## Credits and licensing

Adapted from [faradayfury/printer-all](https://github.com/faradayfury/printer-all),
with its native raster filter derived from Rick Richardson's
[foo2zjs](https://github.com/koenkooi/foo2zjs). JBIG-KIT is by Markus Kuhn.

This repository adds HP 1020 firmware loading to the filter, a dedicated raster
PPD, USB auto-detection and a reproducible installer build. It is a community
project and is not affiliated with HP or Apple.

Driver source is GPL-2.0-or-later; see [LICENSE](LICENSE) and
[THIRD_PARTY.md](THIRD_PARTY.md). The HP firmware is proprietary and is not covered
by the driver's GPL licence; the original notices are preserved in
[src/COPYING](src/COPYING).
