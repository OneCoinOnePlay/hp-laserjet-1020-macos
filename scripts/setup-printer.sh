#!/bin/sh
# Configure only an HP LaserJet 1020 USB queue. GPL-2.0-or-later.
set -eu
queue=HP_LaserJet_1020
ppd=/Library/Printers/PPDs/Contents/Resources/HP-LaserJet-1020-Apple-Silicon.ppd
uri=$(/usr/sbin/lpinfo -v | /usr/bin/awk '$1 == "direct" && $2 ~ /^usb:\/\// && $2 ~ /\/HP%20LaserJet%201020(\?|$)/ {print $2; exit}')
if [ -z "$uri" ]; then
    echo 'Driver installed. Connect and switch on the HP LaserJet 1020, then run:'
    echo 'sudo /Library/Printers/HP1020/setup-printer.sh'
    if [ "${1:-}" = '--optional' ]; then exit 0; fi
    exit 1
fi
default_before=$(/usr/bin/lpstat -d 2>/dev/null | /usr/bin/sed -n 's/^system default destination: //p')
/usr/sbin/lpadmin -p "$queue" -v "$uri" -P "$ppd" -D 'HP LaserJet 1020' -L USB -o printer-is-shared=false -o printer-error-policy=stop-printer -E
/usr/sbin/cupsenable "$queue"
/usr/sbin/cupsaccept "$queue"
if [ -n "$default_before" ] && [ "$default_before" != "$queue" ]; then
    /usr/sbin/lpadmin -d "$default_before"
fi
echo 'Ready: HP LaserJet 1020'
