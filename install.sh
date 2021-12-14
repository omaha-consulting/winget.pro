#!/bin/bash

# Installs winget-private-repository and all dependencies on a fresh Debian 11.
# To use, upload this file and .bashrc to /root, then execute this script as
# root.

# Error handling:
set -e
trap 'echo "Error on line $LINENO"' ERR

################################################################################
#                                  Settings                                    #
################################################################################

chmod 600 .bashrc
source .bashrc

################################################################################
#                                 Settings end                                 #
################################################################################

log() {
    echo -e "\n\033[0;32m`date +%H:%M:%S`\033[0m \033[0;93m$1\033[0m"
}

################################################################################
#                                 Script start                                 #
################################################################################

log 'Setting hostname...'
hostnamectl set-hostname "$HOST_NAME"

log 'Updating system...'
apt-get update > /dev/null
apt-get upgrade -y > /dev/null

log 'Installing iptables-persistent...'
echo iptables-persistent iptables-persistent/autosave_v4 boolean true | debconf-set-selections
echo iptables-persistent iptables-persistent/autosave_v6 boolean true | debconf-set-selections
apt-get -y install iptables-persistent -y > /dev/null

log 'Configuring iptables...'
# Only allow local access to port 25:
iptables -A INPUT -i lo -p tcp --dport 25 -j ACCEPT
iptables -A INPUT -p tcp --dport 25 -j REJECT

# Save iptables rules so they persist across restarts. At the time of this
# writing, there is no open IPv6 port, so enough to save rules.v*4*.
iptables-save > /etc/iptables/rules.v4

log 'Installing git...'
apt-get install git-core -y > /dev/null

log 'Creating application users...'
groupadd --system django
useradd --system --gid django --shell /bin/bash django
mkdir -p /home/django
chown django /home/django
chmod 700 /home/django

log 'Setting up SSH keys. This is required so we can clone the Git repository without having to supply a password...'
mkdir -p .ssh
echo "$GIT_REPO_PUBKEY" > .ssh/id_rsa.pub
chmod 644 .ssh/id_rsa.pub
echo -e "$GIT_REPO_PRIVKEY" > .ssh/id_rsa
chmod 600 .ssh/id_rsa

log 'Adding git repository server to known hosts...'
ssh-keyscan -H ${GIT_SERVER} >> .ssh/known_hosts 2>/dev/null; chmod 600 .ssh/known_hosts

log 'Cloning the repository...'
git clone -q -b ${GIT_REPO_BRANCH} git@${GIT_SERVER}:${GIT_REPO_NAME}.git /srv

log 'Setting up bash profiles...'
ln -sf /srv/conf/.bash_profile .
ln -sf /srv/conf/.bash_profile /home/django
PATH='$PATH' /usr/bin/envsubst < /srv/conf/django.bashrc > /home/django/.bashrc
chown django:django /home/django/.bashrc

log 'Installing Postfix...'
debconf-set-selections <<< "postfix postfix/mailname string $HOST_NAME"
debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
apt-get install postfix mailutils libsasl2-2 ca-certificates libsasl2-modules -y > /dev/null

log 'Configuring Postfix...'
echo "$HOST_NAME" > /etc/mailname
chown postfix /etc/mailname
envsubst '$SMTP_HOST $HOST_NAME' < /srv/conf/postfix/main.cf > /etc/postfix/main.cf
envsubst < /srv/conf/postfix/sasl_passwd > /etc/postfix/sasl_passwd
postmap /etc/postfix/sasl_passwd
chmod 400 /etc/postfix/sasl_passwd
chown postfix /etc/postfix/sasl_passwd
envsubst < /srv/conf/postfix/generic > /etc/postfix/generic
postmap /etc/postfix/generic
chown postfix /etc/postfix/generic
/etc/init.d/postfix reload > /dev/null

log 'Creating data directory...'
# At the moment, we only have a db.sqlite3 file in this directory. It's tempting
# to then just place the file directly into /var/lib. However, this does not
# work, as it leads to file write access errors when SQLite tries to write to
# the database. The reason is probably that SQLite creates additional files in
# the directory.
mkdir -p /var/lib/wpr
chown django:django /var/lib/wpr

log 'Creating directories for static and media files...'
mkdir /srv/static
chown django:django /srv/static
mkdir /srv/media
chown django:django /srv/media

log 'Installing OS dependencies for our Python environment...'
apt-get install python3-venv -y > /dev/null

log 'Creating virtual environment...'
python3 -m venv /srv/venv > /dev/null

log 'Installing Python dependencies...'
# N.B.: pip should be on PATH from sourcing .bashrc at the top.
/srv/venv/bin/pip install -Ur /srv/requirements/base-full.txt > /dev/null

log 'Migrating database...'
su -c '/srv/bin/manage.sh migrate | grep -v "INFO\|DEBUG"' - django

log 'Collecting static files...'
su -c '/srv/bin/manage.sh collectstatic --noinput | grep -v "INFO\|DEBUG"' - django

log 'Initializing run/ directory...'
/srv/omaha/bin/init-run-dir.sh

log 'Installing Supervisor...'
apt-get install supervisor -y > /dev/null

log 'Configuring Supervisor...'
ln -s /srv/conf/gunicorn.conf /etc/supervisor/conf.d

log 'Starting services...'
supervisorctl reread > /dev/null
supervisorctl update > /dev/null

log 'Installing Nginx...'
apt-get install nginx -y > /dev/null

log 'Creating Nginx includes directory...'
mkdir /etc/nginx/includes

log 'Creating Nginx config...'
envsubst < /srv/conf/nginx/server-name > /etc/nginx/includes/server-name
touch /etc/nginx/includes/ssl

log 'Applying Nginx config...'
ln -s /srv/conf/nginx/nginx /etc/nginx/sites-available/wpr
ln -s /etc/nginx/sites-available/wpr /etc/nginx/sites-enabled/wpr
rm /etc/nginx/sites-enabled/default

log 'Starting Nginx...'
service nginx restart

log 'Generating SSL certificates...'
apt-get install certbot python3-certbot-nginx -y > /dev/null
certbot register --quiet --email $ADMIN_EMAIL --agree-tos
certbot certonly --nginx --quiet --cert-name main -d $HOST_NAME
ln -sf /srv/conf/nginx/ssl /etc/nginx/includes/ssl
service nginx restart

log "The server is now serving requests at $HOST_NAME!"

# Now do less important things that are not required for serving requests:

log 'Setting up logrotate...'
ln -s /srv/conf/logrotate /etc/logrotate.d/wpr

log 'Setting up crontab...'
ln -s /srv/bin/cronic /usr/bin/cronic
sed -i "s/\$ADMIN_EMAIL/$ADMIN_EMAIL/g" /srv/conf/crontab
crontab /srv/conf/crontab

log 'Setting up automatic updates...'
apt-get install unattended-upgrades -y > /dev/null
printf 'APT::Periodic::Update-Package-Lists "1";\nAPT::Periodic::Unattended-Upgrade "1";\n' > /etc/apt/apt.conf.d/20auto-upgrades

log 'Done.'