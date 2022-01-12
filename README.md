# simple_py_gadget_reader
*Albert Izard, 2021*

`simple_py_gadget_reader` provides a simple class to read Gadget files in python. Works only with dark-matter particles.

Gadget files are typically composed of multiple files, distinguished by an appended integer ".filenumber" in the filename, where filenumber=[0,n].

Each of them contains a 256-byte header with eg. the number of particles and files. A file is allowed to have 0 particles.

Note that gadget files follow the unformatted binary convention from fortran.
Each data block is preceded and followed by a 32 byte integer specifying the
block size in bytes.

Examples:

```python
import gadget_reader as Gr
gr = Gr.Gadget_reader('/path/to/gadget/files.0')
gr.read_header(verbose=True)
gr.print_npart_all_files()
pos = gr.read_positions_all_files()
```
