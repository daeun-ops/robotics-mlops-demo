#!/usr/bin/env bash
feast apply
feast materialize-incremental $(date +%Y-%m-%d)
