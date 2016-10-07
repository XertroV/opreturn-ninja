#!/bin/bash
echo $0: creating public and private key files

# Create the .ssh directory
mkdir -p ${HOME}/.ssh
chmod 700 ${HOME}/.ssh

# Create the public and private key files from the environment variables.
echo "${HEROKU_PUBLIC_KEY}" > ${HOME}/.ssh/heroku_id_rsa.pub
chmod 644 ${HOME}/.ssh/heroku_id_rsa.pub

# Note use of double quotes, required to preserve newlines
echo "${HEROKU_PRIVATE_KEY}" > ${HOME}/.ssh/heroku_id_rsa
chmod 600 ${HOME}/.ssh/heroku_id_rsa

# Preload the known_hosts file  (see "version 2" below)
echo "bitcoin.xk.io ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPQkI+B0IjWSEydHriSxN/LjwB9MP3YTYNneyJK2zTy9n1z5kmdGhxkhKePSSXUFMOIRhL7gxRbH4hgE33b58I0=" > ${HOME}/.ssh/known_hosts

# Start the SSH tunnel if not already running
SSH_CMD="autossh -M 0 -f -v -o 'ServerAliveInterval 30' -o 'ServerAliveCountMax 3' -i ${HOME}/.ssh/heroku_id_rsa -N -L 8332:127.0.0.1:8332 ${BITCOIN_SSH_USER}@${BITCOIN_HOST}"
echo "SSH_CMD: ${SSH_CMD}"

PID=`pgrep -f "${SSH_CMD}"`
if [ $PID ] ; then
    echo $0: tunnel already running on ${PID}
else
    echo $0 launching tunnel
    $SSH_CMD
fi
