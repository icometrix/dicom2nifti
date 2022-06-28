#!/usr/bin/env bash
echo "Provide version number: "
read GIT_TAG
# Check if tag exists
echo "Check if tag exists ${GIT_TAG}"
if git rev-parse ${GIT_TAG} >/dev/null 2>&1
then
    echo "Duplicate tag found. !!!EXITING!!!"
    exit 1
else
    echo "Creating and pushing tag ${GIT_TAG}."
    git tag ${GIT_TAG}
    git push  --tags git@github.com:icometrix/dicom2nifti.git
    echo "Generating SHA256 for conda forge."
    curl -sL https://github.com/icometrix/dicom2nifti/archive/${GIT_TAG}.tar.gz | openssl sha256
fi

rm -Rf dist
python -m build
twine upload -r pypi dist/*