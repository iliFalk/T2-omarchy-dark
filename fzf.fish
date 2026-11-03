set -l color00 '#1A1A18'
set -l color01 '#EF664D'
set -l color02 '#4AA172'
set -l color03 '#B48A3C'
set -l color04 '#4694EA'
set -l color05 '#A775FF'
set -l color06 '#539D9C'
set -l color07 '#F0EDE5'
set -l color08 '#B4B3AE'
set -l color09 '#FF9B9A'
set -l color0A '#41413E'
set -l color0B '#41413E'
set -l color0C '#79BBFF'
set -l color0D '#F0EDE5'
set -l color0E '#77C1D6'
set -l color0F '#F0EDE5'

set -l FZF_NON_COLOR_OPTS

for arg in (echo $FZF_DEFAULT_OPTS | tr " " "\n")
    if not string match -q -- "--color*" $arg
        set -a FZF_NON_COLOR_OPTS $arg
    end
end

set -Ux FZF_DEFAULT_OPTS "$FZF_NON_COLOR_OPTS"" --color=bg+:$color00,bg:$color00,spinner:$color0E,hl:$color0D"" --color=fg:$color07,header:$color0D,info:$color0A,pointer:$color0E"" --color=marker:$color0E,fg+:$color06,prompt:$color0A,hl+:$color0D"
