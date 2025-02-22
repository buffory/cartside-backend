#!/bin/bash

source ./scripts/bin/activate

echo $1

case $1: in 
    kroger)
        python3 scripts/kroger.py
        ;;
esac