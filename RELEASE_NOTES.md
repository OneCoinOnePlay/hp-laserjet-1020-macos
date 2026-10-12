Native Apple silicon USB printing for the HP LaserJet 1020, confirmed on macOS
27.0.1 with a successful physical test print.

Download `HP-LaserJet-1020-Apple-Silicon.pkg`, connect and power on the printer,
then open the installer. Choose **HP LaserJet 1020** in your print dialog.

- 600 dpi monochrome, A4 by default.
- Automatically detects the connected 1020; no embedded printer serial number.
- Prepends firmware before each job.
- Uses macOS's built-in PDF rendering; no Ghostscript or Rosetta required.
- Preserves an existing default printer.

The installer is unsigned and not notarized. Only a single-page print on the
1020 has been hardware-tested; see the README for the precise testing scope.
Driver source and upstream licence notices are included in the repository.
