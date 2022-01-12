import numpy as np

class Gadget_reader:
    """
    Simple class to read Gadget files in python. Works only with dark-matter particles.

    Gadget files are typically composed of multiple files, distinguished by an
    appended integer ".filenumber" in the filename, where filenumber=[0,n].

    Each of them contains a 256-byte header with eg. the number of particles
    and files. A file is allowed to have 0 particles.

    Note that gadget files follow the unformatted binary convention from fortran.
    Each data block is preceded and followed by a 32 byte integer specifying the
    block size in bytes.
    """

    def __init__(self, filename):
        """
        The filename provided here will be used as default.
        filename must be a complete path to a single gadget file,
        including the filenumber, eg:
        /path/to/file/gadget_file.0
        The some class functions will attempt to find the other files ".i"
        """
        self.filename = filename

        
    def read_header(self, filename=None, verbose=False):
        """
        Read the header of a gadget file.
        verbose: if True print header
        """
        if filename is not None:
            self.filename = filename
        if verbose: print('Reading '+self.filename)

        with open(self.filename, 'rb') as f:
            block_size           = np.fromfile(f, dtype=np.uint32,count=1)[0]
            assert(block_size==256)
            self.npart_this_file = np.fromfile(f, dtype=np.uint32,count=6)[1] # Dark-matter particles
            self.mass            = np.fromfile(f, dtype=np.float64,count=6)[1]
            self.time            = np.fromfile(f, dtype=np.float64,count=1)[0]
            self.redshift        = np.fromfile(f, dtype=np.float64,count=1)[0]
            self.flag_sfr        = np.fromfile(f, dtype=np.int32,count=1)[0]
            self.flag_fb         = np.fromfile(f, dtype=np.int32,count=1)[0]
            self.npart_total     = np.fromfile(f, dtype=np.uint32,count=6)[1] # Experiment with uint vs int
            self.flag_cool       = np.fromfile(f, dtype=np.int32,count=1)[0]
            self.nfiles          = np.fromfile(f, dtype=np.int32,count=1)[0]
            self.boxsize         = np.fromfile(f, dtype=np.float64,count=1)[0]
            self.omega0          = np.fromfile(f, dtype=np.float64,count=1)[0]
            self.omegaL          = np.fromfile(f, dtype=np.float64,count=1)[0]
            self.h               = np.fromfile(f, dtype=np.float64,count=1)[0]

        if verbose:
            v = vars(self)
            for item in v:
                print(f"\t{item:<20}{v[item]}")


    def read_positions(self, filename=None):
        """
        Read dark-matter particle positions into a numpy array
        """
        if filename is not None:
            self.filename = filename

        self.read_header()
        npart = self.npart_this_file

        with open(self.filename, 'rb') as f:
            # Skip header
            f.seek(4+256+4, 0)

            block_size = np.fromfile(f, dtype=np.uint32,count=1)
            if(block_size==0):
                print(f"File {filename} is empty")
                return np.empty((0,3))

            # Determine the floating precision
            bytes_float = block_size / (3*npart)
            if bytes_float==4:
                data_type = np.float32
            elif bytes_float==8:
                data_type = np.float64
            else:
                print(f"block_size: {block_size}, npart_this_file: {npart}, is_double: {is_double}")
                raise RuntimeError('Failed to determine precision for the positions')

            # Read positions
            pos = np.fromfile(f, dtype=data_type, count=3*npart).reshape(npart, 3)

        print(f"{npart} particles positions read")
        return pos


    def read_positions_all_files(self, filename=None):
        """
        Read dark-matter particle positions for all the multiple files
        into a numpy array.
        """

        if filename is not None:
            self.filename = filename

        self.read_header()
        pos = np.empty((0,3))
        npart_read = 0

        # Iterate over files
        for i in range(self.nfiles):
            f = self.filename[:-1]+str(i)
            try:
                p = self.read_positions(f)
                pos = np.append(pos, p, axis=0)
                npart_read += self.npart_this_file
            except:
                print("Error reading positions from " + f)

        print("N particles read from all files: " + str(npart_read))
        return pos


    def print_npart_all_files(self, filename=None):
        """
        Read the headers of all the files and print the number of particles for each
        """

        if filename is not None:
            self.filename = filename

        self.read_header()
        npart_all = 0

        # Iterate over files
        print("\t### Filename ###: \t npart/npart_all")
        for i in range(self.nfiles):
            f = self.filename[:-1]+str(i)
            try:
                self.read_header(f)
                npart_all += self.npart_this_file
            except:
                print("Error reading " + f)

            print("{}: {}/{}".format(f, self.npart_this_file, self.npart_total))

        print("Npart sum across all files: "+str(npart_all))

