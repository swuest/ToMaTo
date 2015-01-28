#!/bin/sh
### BEGIN INIT INFO
# Provides:          tomato-hostmanager
# Required-Start:    $network $local_fs $remote_fs postgresql
# Required-Stop:     $remote_fs postgresql
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: ToMaTo hostmanager
# Description:       This server runs the tomato hostmanager.
### END INIT INFO

# Author: Dennis Schwerdel <schwerdel@informatik.uni-kl.de>

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="ToMaTo hostmanager"           # Introduce a short description here
NAME=tomato-hostmanager             # Introduce the short server's name here
SCRIPTNAME=/etc/init.d/$NAME
LOG=/var/log/tomato/server.log
CERTS_DIR=/etc/tomato/client_certs
CERTS_FILE=/etc/tomato/client_certs.pem

# default settings
USER=root
GROUP=root
UMASK=022

# Exit if the package is not installed
[ -x $DAEMON ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.0-6) to ensure that this file is present.
. /lib/lsb/init-functions

#
# Function that starts the daemon/service
#
do_start()
{
	# Return
	#   0 if daemon has been started
	#   1 if daemon was already running
	#   2 if daemon could not be started
	c_rehash $CERTS_DIR >/dev/null
        cat $CERTS_DIR/*.pem > $CERTS_FILE
	daemon --name=$NAME --user=$USER.$GROUP --running && return 1
	daemon --name=$NAME --user=$USER.$GROUP --umask=$UMASK --output=$LOG -- \
		python /usr/share/tomato-hostmanager/server.py && return 0 || return 2
}

#
# Function that stops the daemon/service
#
do_stop()
{
	# Return
	#   0 if daemon has been stopped
	#   1 if daemon was already stopped
	#   2 if daemon could not be stopped
	#   other if a failure occurred
        daemon --name=$NAME --user=$USER.$GROUP --running || return 1
        daemon --name=$NAME --user=$USER.$GROUP --stop || return 3
        for i in `seq 60`; do
          daemon --name=$NAME --user=$USER.$GROUP --running || return 0
          sleep 1
        done
        return 2
}

#
# Function that sends a SIGHUP to the daemon/service
#
do_reload() {
	#
	# If the daemon can reload its configuration without
	# restarting (for example, when it is sent a SIGHUP),
	# then implement that here.
	#
	return 0
}

case "$1" in
  start)
    [ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC " "$NAME"
    do_start
    case "$?" in
		0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
		2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
	esac
  ;;
  stop)
	[ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
	do_stop
	case "$?" in
		0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
		2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
	esac
	;;
  status)
       daemon -v --name=$NAME --user=$USER.$GROUP --running
       ;;
  #reload|force-reload)
	#
	# If do_reload() is not implemented then leave this commented out
	# and leave 'force-reload' as an alias for 'restart'.
	#
	#log_daemon_msg "Reloading $DESC" "$NAME"
	#do_reload
	#log_end_msg $?
	#;;
  restart|force-reload)
	#
	# If the "reload" option is implemented then remove the
	# 'force-reload' alias
	#
	[ "$VERBOSE" != no ] && log_daemon_msg "Restarting $DESC" "$NAME"
	do_stop
	case "$?" in
	  0|1)
		do_start
		case "$?" in
			0) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
			1) [ "$VERBOSE" != no ] && log_end_msg 1 ;; # Old process is still running
			*) [ "$VERBOSE" != no ] && log_end_msg 1 ;; # Failed to start
		esac
		;;
	  *)
		# Failed to stop
		[ "$VERBOSE" != no ] && log_end_msg 1
		;;
	esac
	;;
  *)
	#echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
	echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload}" >&2
	exit 3
	;;
esac

:
