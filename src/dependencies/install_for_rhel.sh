#!/bin/bash

LOGFILE="install_for_rhel.log"
date >> $LOGFILE

printf "> %-16s" "updating yum" && sudo yum -yqq update && echo "ok" || (echo "failed. Abort." && exit 5 )

printf "> %-16s" "git" && which git >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install git >>$LOGFILE && echo "ok")
printf "> %-16s" "mercurial" && which mercurial >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install mercurial >>$LOGFILE && echo "ok")
printf "> %-16s" "python" && which python >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install python >>$LOGFILE && echo "ok")
printf "> %-16s" "pip" && which python-pip >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install python-dev python-pip >>$LOGFILE && echo "ok")
printf "> %-16s" "perl" && which perl >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install perl >>$LOGFILE && echo "ok")
printf "> %-16s" "scons" && which scons >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install scons >>$LOGFILE && echo "ok")
printf "> %-16s" "openssl" && which openssl >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install openssl >>$LOGFILE && echo "ok")
printf "> %-16s" "postgresql" && which postgresql >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install postgresql* libpq-dev >>$LOGFILE && echo "ok")
printf "> %-16s" "wget" && which wget >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install wget >>$LOGFILE && echo "ok")
printf "> %-16s" "curl" && which curl >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install curl >>$LOGFILE && echo "ok")
printf "> %-16s" "java" && which java >/dev/null 2>&1 && echo "ok" || (echo -n "installing..." && sudo yum -yqq install java-1.8.0-openjdk >>$LOGFILE && echo "ok")
