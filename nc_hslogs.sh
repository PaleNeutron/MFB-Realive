#! /bin/bash
export HSLOGD=/sdcard/Android/data/com.blizzard.wtcg.hearthstone/files/Logs
export last_dir=$(ls -t "${HSLOGD}" | head -n 1)
export zone_file="${HSLOGD}/${last_dir}/Zone.log"
# wait until the file is created
while [ ! -f "${zone_file}" ]; do
  echo "waiting for ${zone_file} to be created"
  sleep 10
done
echo "Starting to tail ${zone_file}"
(cat "${zone_file}" && tail -n 0 -f "${zone_file}")  | nc 192.168.5.9 7777