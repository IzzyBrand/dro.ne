escape ``

startup_message off

# this hard status was stolen from the net, all credit goes to its originator
hardstatus             alwayslastline
#hardstatus string '%{= mK}%-Lw%{= KW}%50>%n%f* %t%{= mK}%+Lw%< %{= kG}%-=%D %d %M %Y %c:%s%{-}'
hardstatus string '%{= kG}[ %{G}%H %{g}][%= %{= kw}%?%-Lw%?%{r}(%{W}%n*%f%t%?(%u)%?%{r})%{w}%?%+Lw%?%?%= %{g}][%{B} %d/%m %{W}%c %{g}]'

# A hint for using multiuser mode:  make sure that both parties have identically
# sized terminals, otherwise there could be graphical mismatches and undrawn text
# for one party :(  .

# turn multiuser mode on so others can connect.
multiuser on

screen -t " vim"
stuff "vim\n"

screen -t " state"

screen -t " test"


