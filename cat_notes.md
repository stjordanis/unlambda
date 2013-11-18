Let's try and construct the unix program `cat`

In the mainloop function, we assume `h` is `<mainloop>`

	<mainloop> = ^h. ``k ``@<parse>i `$h$h
	           = ``s``s`kk ``s``s`k@`k<parse>`ki ``sii
	           = ``s``s`kk ``s``s`k@`k ``s``s``s `k<ifthenelse> i `d`|i `k`d`ei `ki ``sii
	           = ``s``s`kk ``s``s`k@`k ``s``s``s `k``s`kc``s`k`s`k`k`ki``ss`k`kk i `d`|i `k`d`ei `ki ``sii

	<parse> = ^r. ```<ifthenelse> $r `|i `d`ei
	        = ``s``s``s `k<ifthenelse> i `d`|i `k`d`ei

	<runner> = ^x. `$x$x
	         = ``sii

	exec = `<runner><mainloop>
	     = ```sii``s``s`kk ``s``s`k@`k ``s``s``s `k``s`kc``s`k`s`k`k`ki``ss`k`kk i `d`|i `k`d`ei `ki ``sii