#!/bin/bash
set -x
TARGET_DIR="../data/mitmproxy/"
DEST_DIR="../data/mm-capture/"
MITMPROXY2MAHIMAHI="/home/bewo/Projects/mitmproxy2mahimahi/mitmproxy2mahimahi.py"

mkdir -p $TARGET_DIR
for i in `ls ${TARGET_DIR}`; do
	mitmdump -n -q -s "${MITMPROXY2MAHIMAHI} ${DEST_DIR}${i}" -r ${TARGET_DIR}${i}
done
