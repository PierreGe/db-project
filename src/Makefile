all: geodistance.so

%.so: %.c
	gcc -Wall -Wextra -Werror -Wno-unused-function -Wno-unused-parameter -shared -fPIC -o $@ $< -lm 
