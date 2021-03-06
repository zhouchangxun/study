# how bash completion your command arguments ?

## Bash uses the following variables for completion:
```
COMPREPLY: an array containing possible completions as a result of your function
COMP_WORDS: an array containing individual command arguments typed so far
COMP_CWORD: the index of the command argument containing the current cursor position
COMP_LINE: the current command line
```
Therefore, if you want the current argument that you are trying to complete, you would index into the words array using:
  ${COMP_WORDS[COMP_CWORD]}.

So, how do you build the result array COMPREPLY? The easiest way is to use the compgen command.
You can supply a list of words to compgen and a partial word, and it will show you all words that match it.
Let's try it out:
```
sixloop@localhost:~> compgen -W "mars twix twirl" tw
twix
twirl
```

Now we have everything we need to write our completion function:
```
_foo()
{
    local cur=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=( $(compgen -W "alpha beta bar baz" -- $cur) )
}
complete -F _foo foo
```
Save this. Mine is in ~/.bash_completion.d/foo


## Demo
```
sixloop@localhost:~> . ~/.bash_completion.d/foo
sixloop@localhost:~> foo ba[TAB][TAB]
bar
baz
```
