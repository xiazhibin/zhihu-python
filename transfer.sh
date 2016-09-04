#!/bin/bash
for f in *.jpg ; do
    if [[ $(file -b --mime-type "$f") = image/png ]]; then
        mv "$f" "${f/%.jpg/.png}"
    fi
done
