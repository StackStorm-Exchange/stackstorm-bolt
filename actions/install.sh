#!/bin/sh
#
# Instructions copied from https://puppet.com/docs/bolt/0.x/bolt_installing.html

DEBTEST=`lsb_release -a 2> /dev/null | grep Distributor | awk '{print $3}'`
RHTEST=`cat /etc/redhat-release 2> /dev/null | sed -e "s~\(.*\)release.*~\1~g"`

if [[ -n "$RHTEST" ]]; then
  TYPE="rpms"
  echo "*** Detected Distro is ${RHTEST} ***"
  RHMAJVER=`cat /etc/redhat-release | sed 's/[^0-9.]*\([0-9.]\).*/\1/'`
  echo "*** Detected distro version ${RHMAJVER} ***"
  if [[ "$RHMAJVER" != '6' && "$RHMAJVER" != '7' ]]; then
    echo "Unsupported CentOS/Red Hat version $RHMAJVER! Please use 6.x or 7.x!"
    exit 2
  fi
  echo "*** Installing YUM repo ***"
  sudo rpm -Uvh "https://yum.puppet.com/puppet5/puppet5-release-el-$RHMAJVER.noarch.rpm"
  echo "*** Installing Puppet Bolt ***"
  sudo yum -y install puppet-bolt

elif [[ -n "$DEBTEST" ]]; then
  TYPE="debs"
  echo "*** Detected Distro is ${DEBTEST} ***"
  SUBTYPE=`lsb_release -a 2>&1 | grep Codename | grep -v "LSB" | awk '{print $2}'`
  echo "*** Detected flavor ${SUBTYPE} ***"
  if [[ "$SUBTYPE" == 'trusty' ]]; then
    # Ubuntu 14.04 trusty
    echo "*** Installing APT repo ***"
    wget https://apt.puppet.com/puppet5-release-trusty.deb
    sudo dpkg -i puppet5-release-trusty.deb
    sudo apt-get -y update
    echo "*** Installing Puppet Bolt ***"
    sudo apt-get -y install puppet-bolt
  elif [[ "$SUBTYPE" == 'xenial' ]]; then
    # Ubuntu 16.04 trusty
    echo "*** Installing APT repo ***"
    wget https://apt.puppet.com/puppet5-release-xenial.deb
    sudo dpkg -i puppet5-release-xenial.deb
    sudo apt-get -y update
    echo "*** Installing Puppet Bolt ***"
    sudo apt-get -y install puppet-bolt
  else
    echo "Unsupported ubuntu flavor ${SUBTYPE}. Please use 14.04 (trusty) or 16.04 (xenial) as base system!"
    exit 2
  fi
else
  echo "Unknown Operating System! Please use CentOS/Red Hat 6, CentOS/Red Hat 7, Ubuntu 14.04, Ubuntu 16.04"
  exit 2
fi
