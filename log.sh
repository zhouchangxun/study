[root@gateway2 node-slb]# cat log.sh 
#!/bin/bash
# intro: log utilty
# author: sixloop

current_file_name=${BASH_SOURCE[0]}
if [ "$MODULE_LOG" ]; then
   echo "loaded module ${current_file_name} ..."
   return 0;
fi

export MODULE_LOG=1
##########################################################################
cat <<EOF >/dev/null
format: echo -e "\033[${ctrl}\033[${bg};${fg}m ${msg}\033[0m"
\33[0m 关闭所有属性 
\33[01m 设置高亮度 
\33[04m 下划线 
\33[05m 闪烁 
\33[07m 反显 
\33[08m 消隐 
\33[30m -- \33[37m 设置前景色 
\33[40m -- \33[47m 设置背景色 
\33[nA 光标上移n行 
\33[nB 光标下移n行 
\33[nC 光标右移n行 
\33[nD 光标左移n行 
\33[y;xH设置光标位置 
\33[2J 清屏 
\33[K 清除从光标到行尾的内容 
\33[s 保存光标位置 
\33[u 恢复光标位置 
\33[?25l 隐藏光标 
\33[?25h 显示光标
EOF

#control code. 
BOLD="01"             #加粗  
UNDERLINE="04"        #下划线  
BLINK="05"            #闪烁  
  
#foreground color code
FG_GREY="30"          
FG_RED="31"  
FG_GREEN="32"  
FG_YELLOW="33"  
FG_BLUE="34"         
FG_VIOLET="35"      
FG_SKY_BLUE="36"  
FG_WHITE="37"  
  
#background color code 
BG_BLACK="40"  
BG_RED="41"  
BG_GREEN="42"  
BG_YELLOW="43"  
BG_BLUE="44"  
BG_VIOLET="45"  
BG_SKYBLUE="46"  
BG_WHITE="47"  
  
function _coloredlog()  
{  
    msg=$1
    fg=$2
    bg=$3
    ctrl=$4

    control=
    color="\\033[${fg}m"
    restore="\\033[0m"

    if [[ "x$bg" != "x" ]];then
      color="\\033[${bg};${fg}m"
    fi
    if [[ "x$ctrl" != "x" ]];then
      control="\\033[${ctrl}m"
    fi

    echo -e "${control} ${color} ${msg} ${restore}"
}  

function log_debug()  
{  
    msg="$@"
    _coloredlog "[debug]: $msg" $FG_WHITE  
}  
function log_info()  
{  
    msg="$@"
    _coloredlog "[info]: $msg" $FG_GREEN  
}  
function log_warn()  
{  
    msg="$@"
    _coloredlog "[warn]: $msg" $FG_YELLOW 
}  
function log_error()  
{  
    msg="$@"
    _coloredlog "[error]: $msg" $FG_RED $BG_BLACK $UNDERLINE
}  

main(){
echo log module test...
 log="this is a log module test string"  
 log_debug "$log" 1 
 log_info  "$log" 2 
 log_warn  "$log" 3 
 log_error "$log" 4
}

##########################################################################
if [[ "$0" == "$current_file_name" ]] ;then
  main $@
else
  echo "import module ${current_file_name} ..."
fi
