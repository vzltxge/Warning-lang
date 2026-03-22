# 1. Add your new changes
git add .
git commit -m "Finished the new Parser logic"

# 2. Tag this point in time as Version 1.0
git tag -a v1.0 -m "First stable release of Warning-lang"

# 3. Push the code and the tag to GitHub
git push origin main
git push origin v1.0