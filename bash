#!/bin/bash

docker run -v "$PWD":/build -w /build -it snapcore/snapcraft:stable bash
