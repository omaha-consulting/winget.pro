# wpr.sh
# 
# Description: desk for doing work on winget-private-repository
# See https://github.com/jamesob/desk.

# Find the directory this script lies in, even when the script is called via a
# symlink, as per the installation instructions above. Copied from
# http://stackoverflow.com/a/246128/1839209:
if [[ $SHELL == */zsh ]]; then
  SOURCE="$0"
else
  SOURCE="${BASH_SOURCE[0]}"
fi
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
THIS_SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

PROJECT_DIR="$THIS_SCRIPT_DIR/.."

cd "$PROJECT_DIR"
source venv/bin/activate

alias shell='python manage.py shell'
alias release="ssh root@api.winget.pro '/srv/bin/git-update.sh'"
alias migrate="python manage.py migrate"
alias makemigrations="python manage.py makemigrations"
alias tests='python manage.py test'