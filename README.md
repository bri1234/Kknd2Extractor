# Kknd2Extractor
This python scripts are created to extract the sprites and sounds from the KKND2 assets

Compressed file format
======================

LE - little endian
BE - big endian

Header
------

Offset 0:

[4 bytes, unsigned int, LE]     version
[4 bytes, unsigned int, LE]     timestamp
[4 bytes, unsigned int, BE]     uncompressed size in bytes
[4 bytes, unsigned int, LE]     RRLC length (???)

Body
----

Offset 16:

Chunk 0
Chunk 1
...
Chunk N

Chunk:
------

[4 bytes, unsigned int, LE]     chunk uncompressed size in bytes
[4 bytes, unsigned int, LE]     chunk compressed size in bytes (N)

[N bytes]                       Chunk data

to be continued ...

Container file format
=====================

[4 bytes, unsigned int, LE]     absolute offset of file type list

Files
-----

[N10 bytes]                     File list 0 file 0
[N11 bytes]                     File list 0 file 1
...

[N20 bytes]                     File list 1 file 0
[N21 bytes]                     File list 1 file 1
...

File lists
----------

File list 0:

[4 bytes, unsigned int, LE]     Offset file 0
[4 bytes, unsigned int, LE]     Offset file 1
...

File list 1:

[4 bytes, unsigned int, LE]     Offset file 0
[4 bytes, unsigned int, LE]     Offset file 1
...


File type list
--------------

[4 bytes, ASCII]                file type file list 0
[4 bytes, unsigned int, LE]     absolute offset of file list 0
[4 bytes, ASCII]                file type file list 1
[4 bytes, unsigned int, LE]     absolute offset of file list 1
...

[0]                             end of file type list
[0]


