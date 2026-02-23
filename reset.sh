rm -rf .git
git init

git add .
git commit -m "Removed history, due to sensitive data"

git remote add origin git@github.com:biancini/DataScience-HEP.git
git push -u --force origin master
