
test_input is intended to be passed to @. It assumes its argument is i in case an input operation succeeded, or v if it failed, and returns a function that, when applied against an argument F, returns F and prints the appropriate output.

	<test_input> = ^x. ```<ifthenelse> $x <decide> <error1>
	             = ^x. ```<ifthenelse> $x <decide> .E
	             = ``s``s``s `k<ifthenelse> i `k<decide> `k.E
	             = ``s``s``s
			                `k<ifthenelse> # If...
			                i # Condition ($x)
			                `k``s
			                     ``s``s``s # Iftrue (<decide>)
			                              `k<ifthenelse> # If...
			                              `d`?Yi # Condition (currchar == 'Y')
			                              `k.1 # Iftrue (.1)
			                              `d
			                                ```<ifthenelse>
			                                               `d`?Ni
			                                               `k.0
			                                               `k.e
			                     i
			                `k.E # Iffalse (<error1>)

	<error1> = ^x. `.E$x
	         = .E
	<error2> = .e
	<printy> = .1
	<printn> = .0

This function is expanded with the shortcuts `d` and `k`

	<decide> = ^x. ` ```<ifthenelse> `?Yi <printy> ```<ifthenelse> `?Ni <printn> <error2> $x
	         = ``s ``s``s``s `k<ifthenelse> `d`?Yi `k<printy> `d```<ifthenelse> `d`?Ni `k<printn> `k<error2> i
	         = ``s ``s``s``s `k<ifthenelse> `d`?Yi `k.1 `d```<ifthenelse> `d`?Ni `k.0 `k.e i

Let's substitue for <ifthenelse> to obtain:

	``s``s``s
	         `k ``s`kc``s`k`s`k`k`ki``ss`k`kk # If...
	         i # Condition ($x)
	         `k``s
	              ``s``s``s # Iftrue (<decide>)
	                       `k ``s`kc``s`k`s`k`k`ki``ss`k`kk # If...
	                       `d`?Yi # Condition (currchar == 'Y')
	                       `k.1 # Iftrue (.1)
	                       `d
	                         ``` ``s`kc``s`k`s`k`k`ki``ss`k`kk
	                                        `d`?Ni
	                                        `k.0
	                                        `k.e
	              i
	         `k.E # Iffalse (<error1>)

This construct is a function that should have `@` applied to it, and the return value is a printing function:

	``@
	   ``s``s``s
	            `k ``s`kc``s`k`s`k`k`ki``ss`k`kk # If...
	            i # Condition ($x)
	            `k``s
	                 ``s``s``s # Iftrue (<decide>)
	                          `k ``s`kc``s`k`s`k`k`ki``ss`k`kk # If...
	                          `d`?Yi # Condition (currchar == 'Y')
	                          `k.1 # Iftrue (.1)
	                          `d
	                            ``` ``s`kc``s`k`s`k`k`ki``ss`k`kk
	                                           `d`?Ni
	                                           `k.0
	                                           `k.e
	                 i
	            `k.E # Iffalse (<error1>)
	   i