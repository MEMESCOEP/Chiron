#!/bin/bash
APT_PACKAGES=()
WGET_FILES=()

# Parse command-line arguments
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --APT)
            shift
            while [[ $# -gt 0 && ! "$1" =~ -- ]]; do
                APT_PACKAGES+=("$1")
                shift
            done
            ;;
        --WGET)
            shift
            while [[ $# -gt 0 && ! "$1" =~ -- ]]; do
                WGET_FILES+=("$1")
                shift
            done
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Output results
echo "APT Packages: ${APT_PACKAGES[@]}"
echo "WGET Files: ${WGET_FILES[@]}"
echo "${InstallListFile}"
