#!/usr/bin/env bash

apt-get update
apt-get install -y apache2
if ! [ -L varwww ]; then
  rm -rf varwww
  ln -fs vagrant varwww
fi