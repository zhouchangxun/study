#!/bin/bash

DIR="$( cd "$( dirname ${BASH_SOURCE[0]} )" && pwd )"
NAME="$( basename ${BASH_SOURCE[0]} )" 
MODULE=$DIR/$NAME
exe_mode=0

# If the script is sourced by another script
if [ -n "$BASH_SOURCE" -a "$BASH_SOURCE" != "$0" ]
then
  if [ ! $G_MODULES ] ;then  G_MODULES=();fi

  if echo "${G_MODULES[@]}" | grep -w "$MODULE" &>/dev/null; then
    echo "loaded $MODULE";return
  fi

  echo "source [$DIR/$NAME]"
  G_MODULES=(${G_MODULES[@]} $MODULE)
  echo 'loaded modules:' ${G_MODULES[@]}
else # Otherwise, run directly in the shell
  exe_mode=1
  echo execute [$DIR/$NAME]
fi
###############################
# begin: your code
source mod/log.sh
source mod/test2.sh






# end: your code
###############################
main(){
  echo 'execute main(): '$@ 
}

[ $exe_mode = 1 ] &&  main $@
unset main
