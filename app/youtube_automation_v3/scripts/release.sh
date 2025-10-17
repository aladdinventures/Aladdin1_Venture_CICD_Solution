#!/bin/bash
echo "🔖 Preparing GitHub release..."
git tag -a v3.0.0 -m "Stable release v3.0.0 - Aladdin Venture Lab"
git push origin v3.0.0
echo "✅ Release pushed successfully."
