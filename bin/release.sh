#!/bin/bash

# Path to your version.py file
VERSION_FILE="gawsoft/api_client/version.py"

# Read the current version from version.py
CURRENT_VERSION=$(grep -oP '(?<=__version__=")[^"]+' "$VERSION_FILE")

# Increment the patch version
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}
NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"


# Update the version in version.py
sed -i "s/__version__=\"$CURRENT_VERSION\"/__version__=\"$NEW_VERSION\"/" "$VERSION_FILE"

# Commit the change and create a new tag
git add .
git commit -m "Bump version to $NEW_VERSION"
git tag "v$NEW_VERSION"

## Push the new tag to the remote repository
git push origin "v$NEW_VERSION"

echo "Version updated to $NEW_VERSION and tag v$NEW_VERSION pushed to remote repository."
