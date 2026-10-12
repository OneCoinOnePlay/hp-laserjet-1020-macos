# Third-party components

Source was taken from faradayfury/printer-all, downloaded on 12 October 2026.
Upstream main revision recorded that day:
`b6601e32dd6f8958a2e1422264e53cda938269ee`.

- `src/rastertozjs.c`: faradayfury/printer-all native CUPS raster adaptation of
  Rick Richardson's foo2zjs, GPL version 2 or later. Modified on 12 October 2026
  to prepend the HP 1020 firmware, check firmware reads/writes, pause for two
  seconds before page output, and allow a build-time firmware path for validation.
- `src/arm2hpdl.c`, `src/zjs.h`: foo2zjs code, distributed by upstream under GPL;
  original `COPYING` notice is included.
- `src/jbig.c`, `src/jbig.h`, `src/jbig_ar.c`, `src/jbig_ar.h`: JBIG-KIT,
  Copyright Markus Kuhn. GPL version 2 or later; original source notices retained.
- `src/sihp1020.img`: HP proprietary firmware, Copyright HP (2005), as identified
  in upstream `COPYING`. Converted into `sihp1020.dl` by `arm2hpdl` for the installer.
  This file remains HP firmware and is not relicensed under GPL.
- `src/COPYING`: original foo2zjs copyright and licensing notices, unmodified.

The new build script, queue setup scripts and dedicated PPD are provided under
GPL version 2 or later. The complete corresponding driver source accompanies
the installer release in this repository.
